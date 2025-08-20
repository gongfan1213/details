# Selenium详细教程 - 基于Steel-Browser项目实战

## 目录
1. [环境准备](#环境准备)
2. [基础概念](#基础概念)
3. [核心架构](#核心架构)
4. [实战示例](#实战示例)
5. [高级功能](#高级功能)
6. [最佳实践](#最佳实践)
7. [故障排除](#故障排除)

## 环境准备

### 1. 创建项目目录

```bash
# 创建项目目录
mkdir selenium-project
cd selenium-project

# 初始化Node.js项目
npm init -y

# 安装Selenium相关依赖
npm install selenium-webdriver
npm install chromedriver

# 安装TypeScript和开发工具
npm install -D typescript @types/node ts-node
npm install -D @types/selenium-webdriver

# 创建TypeScript配置文件
npx tsc --init
```

### 2. 环境配置

```bash
# 创建.env文件配置环境变量
cat > .env << EOF
SELENIUM_SERVER_URL=http://localhost:4444
CHROME_DRIVER_PATH=./node_modules/chromedriver/lib/chromedriver/chromedriver
CHROME_BINARY_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
EOF
```

### 3. 验证安装

```typescript
import { Builder, By, until } from 'selenium-webdriver';
import * as chrome from 'selenium-webdriver/chrome.js';

async function testSeleniumInstallation() {
  console.log('🚀 测试Selenium安装...');
  
  try {
    // 配置Chrome选项
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    options.addArguments('--disable-dev-shm-usage');
    
    // 创建WebDriver实例
    const driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    // 导航到测试页面
    await driver.get('https://example.com');
    
    // 获取页面标题
    const title = await driver.getTitle();
    console.log(`页面标题: ${title}`);
    
    // 关闭浏览器
    await driver.quit();
    console.log('✅ Selenium安装成功！');
  } catch (error) {
    console.error('❌ Selenium安装失败:', error);
  }
}

testSeleniumInstallation().catch(console.error);
```

## 基础概念

### 1. Selenium核心组件

#### WebDriver
- **ChromeDriver**: Chrome浏览器的WebDriver实现
- **GeckoDriver**: Firefox浏览器的WebDriver实现
- **EdgeDriver**: Edge浏览器的WebDriver实现

#### WebElement
- 页面元素的抽象表示
- 支持点击、输入、获取属性等操作

#### By
- 元素定位策略
- 支持ID、CSS选择器、XPath等多种方式

### 2. Steel-Browser Selenium架构概览

```
Steel-Browser Selenium
├── SeleniumService (Selenium服务)
│   ├── Selenium Server (Selenium服务器)
│   ├── ChromeDriver (Chrome驱动)
│   └── Session Management (会话管理)
├── SessionService (会话服务)
│   ├── Browser Launcher (浏览器启动器)
│   └── Context Manager (上下文管理器)
└── WebDriver Protocol (WebDriver协议)
    ├── HTTP API (HTTP接口)
    └── JSON Wire Protocol (JSON线协议)
```

## 核心架构

### 1. SeleniumService类详解

基于 `steel-browser/api/src/services/selenium.service.ts`：

```typescript
import { EventEmitter } from "events";
import { ChildProcess, spawn } from "child_process";
import { BrowserLauncherOptions, BrowserEvent, BrowserEventType } from "../types/index.js";
import path, { dirname } from "path";
import { FastifyBaseLogger } from "fastify";
import { fileURLToPath } from "url";

export class SeleniumService extends EventEmitter {
  private seleniumProcess: ChildProcess | null = null;
  private seleniumServerUrl: string = "http://localhost:4444";
  private port: number = 4444;
  private launchOptions?: BrowserLauncherOptions;
  private logger: FastifyBaseLogger;

  constructor(logger: FastifyBaseLogger) {
    super();
    this.logger = logger;
  }

  public async getChromeArgs(): Promise<string[]> {
    const { options, userAgent } = this.launchOptions ?? {};
    return [
      "disable-dev-shm-usage",
      "no-sandbox",
      "enable-javascript",
      userAgent ? `user-agent=${userAgent}` : "",
      options?.proxyUrl ? `proxy-server=${options.proxyUrl}` : "",
      ...(options?.args?.map((arg) => (arg.startsWith("--") ? arg.slice(2) : arg)) || []),
    ].filter(Boolean);
  }

  public async launch(launchOptions: BrowserLauncherOptions): Promise<void> {
    this.launchOptions = launchOptions;

    if (this.seleniumProcess) {
      await this.close();
    }

    const projectRoot = path.resolve(dirname(fileURLToPath(import.meta.url)), "../../");
    const seleniumServerPath = path.join(projectRoot, "selenium", "server", "selenium-server.jar");

    const seleniumArgs = ["-jar", seleniumServerPath, "standalone"];

    this.seleniumProcess = spawn("java", seleniumArgs);
    this.seleniumServerUrl = `http://localhost:${this.port}`;

    this.seleniumProcess.stdout?.on("data", (data) => {
      this.logger.info(`Selenium stdout: ${data}`);
      this.postLog({
        type: BrowserEventType.Console,
        text: JSON.stringify({ type: BrowserEventType.Console, message: `${data}` }),
        timestamp: new Date(),
      });
    });

    this.seleniumProcess.stderr?.on("data", (data) => {
      this.logger.error(`Selenium stderr: ${data}`);
      this.postLog({
        type: BrowserEventType.Error,
        text: JSON.stringify({ type: BrowserEventType.Error, error: `${data}` }),
        timestamp: new Date(),
      });
    });

    this.seleniumProcess.on("close", (code) => {
      this.logger.info(`Selenium process exited with code ${code}`);
      this.seleniumProcess = null;
    });

    await new Promise<void>((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error("Selenium server failed to start within the timeout period"));
      }, 15000); // 15 seconds timeout

      this.seleniumProcess!.stdout?.on("data", (data) => {
        if (data.toString().includes("Started Selenium Standalone")) {
          clearTimeout(timeout);
          resolve();
        }
      });
    });
  }

  public close(): void {
    if (this.seleniumProcess) {
      this.seleniumProcess.kill("SIGINT");
      this.seleniumProcess = null;
    }
  }

  public getSeleniumServerUrl(): string {
    return this.seleniumServerUrl;
  }

  private async postLog(browserLog: BrowserEvent) {
    if (!this.launchOptions?.logSinkUrl) {
      return;
    }
    await fetch(this.launchOptions.logSinkUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(browserLog),
    });
  }
}
```

### 2. 会话管理示例

基于 `steel-browser/api/src/services/session.service.ts`：

```typescript
import { SessionService } from "./session.service.js";
import { SeleniumService } from "./selenium.service.js";

export class SessionService {
  private logger: FastifyBaseLogger;
  private cdpService: CDPService;
  private seleniumService: SeleniumService;
  private activeSession: SessionDetails;

  constructor(config: {
    cdpService: CDPService;
    seleniumService: SeleniumService;
  }) {
    this.logger = config.logger;
    this.cdpService = config.cdpService;
    this.seleniumService = config.seleniumService;
    this.activeSession = new SessionDetails();
  }

  public async startSession(options: {
    sessionId?: string;
    proxyUrl?: string;
    userAgent?: string;
    sessionContext?: {
      cookies?: CookieData[];
      localStorage?: Record<string, Record<string, any>>;
    };
    isSelenium?: boolean;
    logSinkUrl?: string;
    blockAds?: boolean;
    extensions?: string[];
    timezone?: string;
    dimensions?: { width: number; height: number };
    extra?: Record<string, Record<string, string>>;
    credentials: CredentialsOptions;
    skipFingerprintInjection?: boolean;
    userPreferences?: Record<string, any>;
  }): Promise<SessionDetails> {
    
    const {
      sessionId,
      proxyUrl,
      userAgent,
      sessionContext,
      isSelenium = false,
      logSinkUrl,
      blockAds,
      extensions,
      timezone,
      dimensions,
      extra,
      credentials,
      skipFingerprintInjection,
      userPreferences,
    } = options;

    const defaultUserPreferences = {
      plugins: {
        always_open_pdf_externally: true,
        plugins_disabled: ["Chrome PDF Viewer"],
      },
    };

    const mergedUserPreferences = userPreferences
      ? deepMerge(defaultUserPreferences, userPreferences)
      : defaultUserPreferences;

    const browserLauncherOptions: BrowserLauncherOptions = {
      options: {
        headless: env.CHROME_HEADLESS,
        proxyUrl: this.activeSession.proxyServer?.url,
      },
      sessionContext,
      userAgent,
      blockAds,
      extensions: extensions || [],
      logSinkUrl,
      timezone: timezonePromise,
      dimensions,
      userDataDir,
      userPreferences: mergedUserPreferences,
      extra,
      credentials,
      skipFingerprintInjection,
    };

    if (isSelenium) {
      await this.cdpService.shutdown();
      await this.seleniumService.launch(browserLauncherOptions);

      Object.assign(this.activeSession, {
        websocketUrl: "",
        debugUrl: "",
        sessionViewerUrl: "",
        userAgent:
          userAgent ||
          "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
      });

      return this.activeSession;
    } else {
      await this.cdpService.startNewSession(browserLauncherOptions);

      Object.assign(this.activeSession, {
        websocketUrl: getBaseUrl("ws"),
        debugUrl: getUrl("v1/sessions/debug"),
        debuggerUrl: getUrl("v1/devtools/inspector.html"),
        sessionViewerUrl: getBaseUrl(),
        userAgent:
          this.cdpService.getUserAgent() ||
          "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
      });
    }

    return this.activeSession;
  }

  public async endSession(): Promise<SessionDetails> {
    this.activeSession.complete();
    
    if (this.activeSession.isSelenium) {
      this.seleniumService.close();
    } else {
      await this.cdpService.shutdown();
    }
    
    return this.activeSession;
  }
}
```

## 实战示例

### 1. 基础搜索示例

```typescript
import { Builder, By, until, WebDriver } from 'selenium-webdriver';
import * as chrome from 'selenium-webdriver/chrome.js';

async function basicSearchExample() {
  console.log('🔍 开始基础搜索示例...');
  
  let driver: WebDriver;
  
  try {
    // 配置Chrome选项
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    options.addArguments('--disable-dev-shm-usage');
    options.addArguments('--disable-blink-features=AutomationControlled');
    
    // 创建WebDriver实例
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    // 设置窗口大小
    await driver.manage().window().setRect({ width: 1280, height: 800 });
    
    // 导航到百度
    console.log('🌐 导航到百度首页...');
    await driver.get('https://www.baidu.com');
    
    // 等待搜索框加载
    const searchBox = await driver.wait(until.elementLocated(By.id('kw')), 10000);
    
    // 输入搜索关键词
    console.log('🔍 搜索"Selenium教程"...');
    await searchBox.sendKeys('Selenium教程');
    
    // 点击搜索按钮
    const searchButton = await driver.findElement(By.id('su'));
    await searchButton.click();
    
    // 等待搜索结果加载
    await driver.wait(until.elementLocated(By.id('content_left')), 10000);
    
    // 获取搜索结果
    const searchResults = await driver.findElements(By.css('.result'));
    
    console.log('📋 搜索结果:');
    for (let i = 0; i < Math.min(searchResults.length, 5); i++) {
      const result = searchResults[i];
      
      try {
        const titleElement = await result.findElement(By.css('h3'));
        const title = await titleElement.getText();
        
        const linkElement = await result.findElement(By.css('a'));
        const link = await linkElement.getAttribute('href');
        
        const snippetElement = await result.findElement(By.css('.c-abstract'));
        const snippet = await snippetElement.getText();
        
        console.log(`${i + 1}. ${title}`);
        console.log(`   链接: ${link}`);
        console.log(`   摘要: ${snippet.substring(0, 100)}...`);
        console.log('');
      } catch (error) {
        console.log(`结果 ${i + 1}: 解析失败`);
      }
    }
    
    // 截图保存
    const screenshot = await driver.takeScreenshot();
    const fs = require('fs');
    fs.writeFileSync('search_results.png', screenshot, 'base64');
    console.log('📸 截图已保存为 search_results.png');
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}

basicSearchExample().catch(console.error);
```

### 2. 表单填写示例

```typescript
import { Builder, By, until, WebDriver } from 'selenium-webdriver';
import * as chrome from 'selenium-webdriver/chrome.js';

async function formFillingExample() {
  console.log('📝 开始表单填写示例...');
  
  let driver: WebDriver;
  
  try {
    // 配置Chrome选项
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    options.addArguments('--disable-dev-shm-usage');
    
    // 创建WebDriver实例
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    // 导航到测试表单页面
    await driver.get('https://httpbin.org/forms/post');
    
    // 等待页面加载
    await driver.wait(until.elementLocated(By.name('custname')), 10000);
    
    // 填写表单字段
    console.log('✍️ 填写表单...');
    
    await driver.findElement(By.name('custname')).sendKeys('张三');
    await driver.findElement(By.name('custtel')).sendKeys('138-1234-5678');
    await driver.findElement(By.name('custemail')).sendKeys('zhangsan@example.com');
    
    // 选择下拉菜单
    const sizeSelect = await driver.findElement(By.name('size'));
    await sizeSelect.findElement(By.css('option[value="medium"]')).click();
    
    const toppingSelect = await driver.findElement(By.name('topping'));
    await toppingSelect.findElement(By.css('option[value="cheese"]')).click();
    
    const deliverySelect = await driver.findElement(By.name('delivery'));
    await deliverySelect.findElement(By.css('option[value="now"]')).click();
    
    // 填写备注
    await driver.findElement(By.name('comments')).sendKeys('这是一个测试表单提交');
    
    // 提交表单
    console.log('📤 提交表单...');
    await driver.findElement(By.css('input[type="submit"]')).click();
    
    // 等待响应页面加载
    await driver.wait(until.elementLocated(By.tagName('pre')), 10000);
    
    // 获取响应内容
    const responseElement = await driver.findElement(By.tagName('pre'));
    const responseText = await responseElement.getText();
    console.log('📄 表单提交响应:');
    console.log(responseText);
    
    // 截图保存
    const screenshot = await driver.takeScreenshot();
    const fs = require('fs');
    fs.writeFileSync('form_response.png', screenshot, 'base64');
    console.log('📸 响应截图已保存为 form_response.png');
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}

formFillingExample().catch(console.error);
```

### 3. 数据提取示例

```typescript
import { Builder, By, until, WebDriver } from 'selenium-webdriver';
import * as chrome from 'selenium-webdriver/chrome.js';
import * as fs from 'fs';

async function dataExtractionExample() {
  console.log('📊 开始数据提取示例...');
  
  let driver: WebDriver;
  
  try {
    // 配置Chrome选项
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    options.addArguments('--disable-dev-shm-usage');
    
    // 创建WebDriver实例
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    // 导航到新闻网站
    await driver.get('https://news.ycombinator.com');
    
    // 等待页面加载
    await driver.wait(until.elementLocated(By.css('.athing')), 10000);
    
    // 提取新闻标题和链接
    console.log('📰 提取新闻数据...');
    const newsElements = await driver.findElements(By.css('.athing'));
    
    const newsData = [];
    for (let i = 0; i < Math.min(newsElements.length, 10); i++) {
      const element = newsElements[i];
      
      try {
        const titleElement = await element.findElement(By.css('.titleline a'));
        const title = await titleElement.getText();
        const link = await titleElement.getAttribute('href');
        
        // 获取分数和作者信息
        const nextElement = await driver.executeScript(
          'return arguments[0].nextElementSibling;', 
          element
        );
        
        let score = '0 points';
        let author = 'Unknown';
        
        if (nextElement) {
          try {
            const scoreElement = await nextElement.findElement(By.css('.score'));
            score = await scoreElement.getText();
          } catch (error) {
            // 忽略错误
          }
          
          try {
            const authorElement = await nextElement.findElement(By.css('.hnuser'));
            author = await authorElement.getText();
          } catch (error) {
            // 忽略错误
          }
        }
        
        newsData.push({
          title,
          link,
          score,
          author
        });
        
        console.log(`${i + 1}. ${title}`);
        console.log(`   分数: ${score} | 作者: ${author}`);
        console.log(`   链接: ${link}`);
        console.log('');
        
      } catch (error) {
        console.log(`新闻 ${i + 1}: 解析失败`);
      }
    }
    
    // 保存数据到JSON文件
    const jsonData = JSON.stringify(newsData, null, 2);
    fs.writeFileSync('news_data.json', jsonData);
    console.log('💾 数据已保存到 news_data.json');
    
    // 生成CSV格式
    const csvHeader = 'Title,Score,Author,Link\n';
    const csvRows = newsData.map(item => 
      `"${item.title}","${item.score}","${item.author}","${item.link}"`
    ).join('\n');
    const csvData = csvHeader + csvRows;
    fs.writeFileSync('news_data.csv', csvData);
    console.log('💾 数据已保存到 news_data.csv');
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}

dataExtractionExample().catch(console.error);
```

## 高级功能

### 1. 等待策略

```typescript
import { Builder, By, until, WebDriver } from 'selenium-webdriver';
import * as chrome from 'selenium-webdriver/chrome.js';

async function waitStrategiesExample() {
  let driver: WebDriver;
  
  try {
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    await driver.get('https://example.com');
    
    // 1. 显式等待 - 等待元素出现
    const element = await driver.wait(until.elementLocated(By.id('my-element')), 10000);
    
    // 2. 显式等待 - 等待元素可见
    await driver.wait(until.elementIsVisible(element), 10000);
    
    // 3. 显式等待 - 等待元素可点击
    await driver.wait(until.elementIsEnabled(element), 10000);
    
    // 4. 显式等待 - 等待文本出现
    await driver.wait(until.elementTextContains(element, 'expected text'), 10000);
    
    // 5. 显式等待 - 等待页面标题
    await driver.wait(until.titleIs('Expected Title'), 10000);
    
    // 6. 显式等待 - 等待URL变化
    await driver.wait(until.urlContains('expected-url'), 10000);
    
    // 7. 自定义等待条件
    await driver.wait(async () => {
      const elements = await driver.findElements(By.css('.dynamic-content'));
      return elements.length > 0;
    }, 10000);
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}
```

### 2. 键盘和鼠标操作

```typescript
import { Builder, By, until, WebDriver, Key, Actions } from 'selenium-webdriver';
import * as chrome from 'selenium-webdriver/chrome.js';

async function keyboardMouseExample() {
  let driver: WebDriver;
  
  try {
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    await driver.get('https://example.com');
    
    const actions = new Actions(driver);
    
    // 键盘操作
    const inputElement = await driver.findElement(By.css('input[type="text"]'));
    
    // 输入文本
    await inputElement.sendKeys('Hello World');
    
    // 组合键操作
    await inputElement.sendKeys(Key.CONTROL, 'a'); // 全选
    await inputElement.sendKeys(Key.DELETE); // 删除
    
    // 特殊键
    await inputElement.sendKeys('Text with', Key.ENTER, 'new line');
    
    // 鼠标操作
    const targetElement = await driver.findElement(By.css('.target-element'));
    
    // 鼠标悬停
    await actions.move({ origin: targetElement }).perform();
    
    // 鼠标点击
    await actions.click(targetElement).perform();
    
    // 双击
    await actions.doubleClick(targetElement).perform();
    
    // 右键点击
    await actions.contextClick(targetElement).perform();
    
    // 拖拽操作
    const sourceElement = await driver.findElement(By.css('.source-element'));
    const destinationElement = await driver.findElement(By.css('.destination-element'));
    
    await actions
      .dragAndDrop(sourceElement, destinationElement)
      .perform();
    
    // 滚动操作
    await driver.executeScript('window.scrollTo(0, 500);');
    
    // 滚动到元素
    await driver.executeScript('arguments[0].scrollIntoView(true);', targetElement);
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}
```

### 3. 多窗口和框架处理

```typescript
import { Builder, By, until, WebDriver } from 'selenium-webdriver';
import * as chrome from 'selenium-webdriver/chrome.js';

async function multiWindowFrameExample() {
  let driver: WebDriver;
  
  try {
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    await driver.get('https://example.com');
    
    // 获取当前窗口句柄
    const originalWindow = await driver.getWindowHandle();
    
    // 打开新窗口
    await driver.executeScript('window.open("https://google.com", "_blank");');
    
    // 获取所有窗口句柄
    const windowHandles = await driver.getAllWindowHandles();
    
    // 切换到新窗口
    for (const handle of windowHandles) {
      if (handle !== originalWindow) {
        await driver.switchTo().window(handle);
        break;
      }
    }
    
    // 在新窗口中操作
    await driver.findElement(By.name('q')).sendKeys('Selenium WebDriver');
    
    // 切换回原窗口
    await driver.switchTo().window(originalWindow);
    
    // 处理iframe
    await driver.get('https://example.com/iframe-page');
    
    // 切换到iframe
    const iframe = await driver.findElement(By.css('iframe'));
    await driver.switchTo().frame(iframe);
    
    // 在iframe中操作
    await driver.findElement(By.css('.iframe-content')).click();
    
    // 切换回主文档
    await driver.switchTo().defaultContent();
    
    // 关闭新窗口
    await driver.switchTo().window(windowHandles[1]);
    await driver.close();
    
    // 切换回原窗口
    await driver.switchTo().window(originalWindow);
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}
```

### 4. 文件上传和下载

```typescript
import { Builder, By, until, WebDriver } from 'selenium-webdriver';
import * as chrome from 'selenium-webdriver/chrome.js';
import * as fs from 'fs';
import * as path from 'path';

async function fileUploadDownloadExample() {
  let driver: WebDriver;
  
  try {
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    
    // 设置下载目录
    const downloadDir = path.join(process.cwd(), 'downloads');
    if (!fs.existsSync(downloadDir)) {
      fs.mkdirSync(downloadDir);
    }
    
    options.setUserPreferences({
      'download.default_directory': downloadDir,
      'download.prompt_for_download': false,
      'download.directory_upgrade': true,
      'safebrowsing.enabled': true
    });
    
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    // 文件上传示例
    await driver.get('https://example.com/upload');
    
    const fileInput = await driver.findElement(By.css('input[type="file"]'));
    const filePath = path.join(process.cwd(), 'test-file.txt');
    
    // 创建测试文件
    fs.writeFileSync(filePath, 'This is a test file for upload');
    
    // 上传文件
    await fileInput.sendKeys(filePath);
    
    // 点击上传按钮
    await driver.findElement(By.css('input[type="submit"]')).click();
    
    // 等待上传完成
    await driver.wait(until.elementLocated(By.css('.upload-success')), 10000);
    
    // 文件下载示例
    await driver.get('https://example.com/download');
    
    // 点击下载链接
    await driver.findElement(By.css('.download-link')).click();
    
    // 等待下载完成
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 检查下载的文件
    const downloadedFiles = fs.readdirSync(downloadDir);
    console.log('下载的文件:', downloadedFiles);
    
    // 清理测试文件
    fs.unlinkSync(filePath);
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}
```

### 5. 截图和日志记录

```typescript
import { Builder, By, until, WebDriver } from 'selenium-webdriver';
import * as chrome from 'selenium-webdriver/chrome.js';
import * as fs from 'fs';

async function screenshotLoggingExample() {
  let driver: WebDriver;
  
  try {
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    
    // 启用日志记录
    options.setLoggingPrefs({
      browser: 'ALL',
      driver: 'ALL'
    });
    
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    await driver.get('https://example.com');
    
    // 获取浏览器日志
    const browserLogs = await driver.manage().logs().get('browser');
    console.log('浏览器日志:', browserLogs);
    
    // 获取驱动日志
    const driverLogs = await driver.manage().logs().get('driver');
    console.log('驱动日志:', driverLogs);
    
    // 截图
    const screenshot = await driver.takeScreenshot();
    fs.writeFileSync('full_page_screenshot.png', screenshot, 'base64');
    
    // 元素截图
    const element = await driver.findElement(By.css('.target-element'));
    const elementScreenshot = await element.takeScreenshot();
    fs.writeFileSync('element_screenshot.png', elementScreenshot, 'base64');
    
    // 页面源码
    const pageSource = await driver.getPageSource();
    fs.writeFileSync('page_source.html', pageSource);
    
    console.log('✅ 截图和日志记录完成');
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}
```

## 最佳实践

### 1. 页面对象模式 (POM)

```typescript
// BasePage.ts
import { WebDriver, By, until } from 'selenium-webdriver';

export abstract class BasePage {
  protected driver: WebDriver;
  
  constructor(driver: WebDriver) {
    this.driver = driver;
  }
  
  abstract getPageUrl(): string;
  
  async navigateTo(): Promise<void> {
    await this.driver.get(this.getPageUrl());
  }
  
  async waitForPageLoad(): Promise<void> {
    await this.driver.wait(until.titleIs(await this.driver.getTitle()), 10000);
  }
  
  async takeScreenshot(filename: string): Promise<void> {
    const screenshot = await this.driver.takeScreenshot();
    const fs = require('fs');
    fs.writeFileSync(filename, screenshot, 'base64');
  }
}

// SearchPage.ts
import { By, until } from 'selenium-webdriver';
import { BasePage } from './BasePage';

export class SearchPage extends BasePage {
  private searchBox = By.id('kw');
  private searchButton = By.id('su');
  private searchResults = By.css('.result');
  
  getPageUrl(): string {
    return 'https://www.baidu.com';
  }
  
  async search(keyword: string): Promise<void> {
    const searchInput = await this.driver.findElement(this.searchBox);
    await searchInput.clear();
    await searchInput.sendKeys(keyword);
    await this.driver.findElement(this.searchButton).click();
  }
  
  async getSearchResults(): Promise<string[]> {
    await this.driver.wait(until.elementLocated(this.searchResults), 10000);
    const results = await this.driver.findElements(this.searchResults);
    
    return Promise.all(
      results.map(async (result) => {
        const titleElement = await result.findElement(By.css('h3'));
        return await titleElement.getText();
      })
    );
  }
}

// 使用页面对象
async function pageObjectExample() {
  let driver: WebDriver;
  
  try {
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    const searchPage = new SearchPage(driver);
    await searchPage.navigateTo();
    await searchPage.search('Selenium WebDriver');
    
    const results = await searchPage.getSearchResults();
    console.log('搜索结果:', results);
    
    await searchPage.takeScreenshot('search_results.png');
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}
```

### 2. 数据驱动测试

```typescript
// TestData.ts
export interface TestData {
  keyword: string;
  expectedResults: number;
  description: string;
}

export const searchTestData: TestData[] = [
  {
    keyword: 'Selenium WebDriver',
    expectedResults: 5,
    description: '搜索Selenium WebDriver'
  },
  {
    keyword: 'Python自动化',
    expectedResults: 3,
    description: '搜索Python自动化'
  },
  {
    keyword: 'JavaScript测试',
    expectedResults: 4,
    description: '搜索JavaScript测试'
  }
];

// DataDrivenTest.ts
import { Builder, By, until, WebDriver } from 'selenium-webdriver';
import * as chrome from 'selenium-webdriver/chrome.js';
import { searchTestData, TestData } from './TestData';

async function dataDrivenSearchTest() {
  let driver: WebDriver;
  
  try {
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    for (const testData of searchTestData) {
      console.log(`🧪 执行测试: ${testData.description}`);
      
      await driver.get('https://www.baidu.com');
      
      const searchBox = await driver.findElement(By.id('kw'));
      await searchBox.clear();
      await searchBox.sendKeys(testData.keyword);
      
      await driver.findElement(By.id('su')).click();
      
      await driver.wait(until.elementLocated(By.css('.result')), 10000);
      
      const results = await driver.findElements(By.css('.result'));
      
      const actualResults = results.length;
      const passed = actualResults >= testData.expectedResults;
      
      console.log(`   关键词: ${testData.keyword}`);
      console.log(`   期望结果数: ${testData.expectedResults}`);
      console.log(`   实际结果数: ${actualResults}`);
      console.log(`   测试结果: ${passed ? '✅ 通过' : '❌ 失败'}`);
      console.log('');
      
      // 截图
      const screenshot = await driver.takeScreenshot();
      const fs = require('fs');
      fs.writeFileSync(
        `search_${testData.keyword.replace(/\s+/g, '_')}.png`, 
        screenshot, 
        'base64'
      );
    }
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}
```

### 3. 测试框架集成

```typescript
// SeleniumTestFramework.ts
import { Builder, By, until, WebDriver } from 'selenium-webdriver';
import * as chrome from 'selenium-webdriver/chrome.js';

export class SeleniumTestFramework {
  private driver: WebDriver | null = null;
  private testResults: TestResult[] = [];
  
  async setup(): Promise<void> {
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    options.addArguments('--headless'); // 无头模式
    
    this.driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
  }
  
  async teardown(): Promise<void> {
    if (this.driver) {
      await this.driver.quit();
      this.driver = null;
    }
  }
  
  async runTest(testName: string, testFunction: (driver: WebDriver) => Promise<void>): Promise<void> {
    if (!this.driver) {
      throw new Error('Driver not initialized');
    }
    
    const startTime = Date.now();
    let passed = false;
    let error: Error | null = null;
    
    try {
      await testFunction(this.driver);
      passed = true;
    } catch (err) {
      error = err as Error;
      passed = false;
      
      // 截图
      if (this.driver) {
        const screenshot = await this.driver.takeScreenshot();
        const fs = require('fs');
        fs.writeFileSync(`error_${testName}.png`, screenshot, 'base64');
      }
    }
    
    const duration = Date.now() - startTime;
    
    this.testResults.push({
      name: testName,
      passed,
      duration,
      error: error?.message || null
    });
    
    console.log(`${passed ? '✅' : '❌'} ${testName} (${duration}ms)`);
    if (error) {
      console.error(`   错误: ${error.message}`);
    }
  }
  
  getTestResults(): TestResult[] {
    return this.testResults;
  }
  
  generateReport(): void {
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(r => r.passed).length;
    const failedTests = totalTests - passedTests;
    
    console.log('\n📊 测试报告');
    console.log('=' * 50);
    console.log(`总测试数: ${totalTests}`);
    console.log(`通过: ${passedTests}`);
    console.log(`失败: ${failedTests}`);
    console.log(`成功率: ${((passedTests / totalTests) * 100).toFixed(2)}%`);
    
    if (failedTests > 0) {
      console.log('\n❌ 失败的测试:');
      this.testResults
        .filter(r => !r.passed)
        .forEach(r => {
          console.log(`  - ${r.name}: ${r.error}`);
        });
    }
  }
}

interface TestResult {
  name: string;
  passed: boolean;
  duration: number;
  error: string | null;
}

// 使用测试框架
async function frameworkExample() {
  const framework = new SeleniumTestFramework();
  
  try {
    await framework.setup();
    
    // 运行测试
    await framework.runTest('百度搜索测试', async (driver) => {
      await driver.get('https://www.baidu.com');
      await driver.findElement(By.id('kw')).sendKeys('Selenium');
      await driver.findElement(By.id('su')).click();
      await driver.wait(until.elementLocated(By.css('.result')), 10000);
    });
    
    await framework.runTest('表单填写测试', async (driver) => {
      await driver.get('https://httpbin.org/forms/post');
      await driver.findElement(By.name('custname')).sendKeys('Test User');
      await driver.findElement(By.css('input[type="submit"]')).click();
      await driver.wait(until.elementLocated(By.tagName('pre')), 10000);
    });
    
    // 生成报告
    framework.generateReport();
    
  } finally {
    await framework.teardown();
  }
}
```

## 故障排除

### 1. 常见错误及解决方案

```typescript
// 1. WebDriver启动失败
async function handleWebDriverError() {
  try {
    const driver = await new Builder()
      .forBrowser('chrome')
      .build();
  } catch (error) {
    console.error('WebDriver启动失败:', error);
    
    // 解决方案1: 检查ChromeDriver路径
    const driver = await new Builder()
      .forBrowser('chrome')
      .setChromeService(new chrome.ServiceBuilder('/path/to/chromedriver'))
      .build();
    
    // 解决方案2: 使用系统ChromeDriver
    const driver = await new Builder()
      .forBrowser('chrome')
      .build();
  }
}

// 2. 元素定位失败
async function handleElementNotFound(driver: WebDriver) {
  try {
    await driver.findElement(By.id('non-existent-element'));
  } catch (error) {
    console.error('元素未找到:', error);
    
    // 解决方案1: 使用显式等待
    await driver.wait(until.elementLocated(By.id('non-existent-element')), 10000);
    
    // 解决方案2: 使用JavaScript查找
    const element = await driver.executeScript(
      'return document.getElementById("non-existent-element");'
    );
    
    // 解决方案3: 使用更灵活的选择器
    const elements = await driver.findElements(By.css('[data-testid*="element"]'));
  }
}

// 3. 页面加载超时
async function handlePageLoadTimeout(driver: WebDriver) {
  try {
    await driver.get('https://slow-loading-site.com');
  } catch (error) {
    console.error('页面加载超时:', error);
    
    // 解决方案1: 增加页面加载超时
    await driver.manage().setTimeouts({ pageLoad: 60000 });
    await driver.get('https://slow-loading-site.com');
    
    // 解决方案2: 使用JavaScript检查页面状态
    await driver.executeScript(`
      return new Promise((resolve) => {
        if (document.readyState === 'complete') {
          resolve();
        } else {
          window.addEventListener('load', resolve);
        }
      });
    `);
  }
}
```

### 2. 性能优化

```typescript
async function optimizedSeleniumExample() {
  let driver: WebDriver;
  
  try {
    const options = new chrome.Options();
    
    // 性能优化选项
    options.addArguments(
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--disable-background-timer-throttling',
      '--disable-backgrounding-occluded-windows',
      '--disable-renderer-backgrounding',
      '--disable-features=TranslateUI',
      '--disable-ipc-flooding-protection',
      '--memory-pressure-off',
      '--max_old_space_size=4096'
    );
    
    // 禁用图片和CSS加载
    options.addArguments('--blink-settings=imagesEnabled=false');
    
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    // 设置页面加载策略
    await driver.manage().setTimeouts({
      pageLoad: 30000,
      script: 30000,
      implicit: 10000
    });
    
    // 禁用图片加载
    await driver.executeScript(`
      const images = document.querySelectorAll('img');
      images.forEach(img => img.style.display = 'none');
    `);
    
    await driver.get('https://example.com');
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}
```

### 3. 调试技巧

```typescript
async function debugSeleniumExample() {
  let driver: WebDriver;
  
  try {
    const options = new chrome.Options();
    options.addArguments('--no-sandbox');
    
    // 启用详细日志
    options.setLoggingPrefs({
      browser: 'ALL',
      driver: 'ALL'
    });
    
    driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build();
    
    // 监听控制台日志
    const logs = await driver.manage().logs();
    logs.get('browser').then((browserLogs) => {
      browserLogs.forEach((log) => {
        console.log('浏览器日志:', log.message);
      });
    });
    
    // 添加调试信息
    await driver.executeScript(`
      console.log('页面URL:', window.location.href);
      console.log('页面标题:', document.title);
      console.log('DOM元素数量:', document.querySelectorAll('*').length);
    `);
    
    // 高亮元素
    await driver.executeScript(`
      const element = document.querySelector('.target-element');
      if (element) {
        element.style.border = '3px solid red';
        element.style.backgroundColor = 'yellow';
      }
    `);
    
    await driver.get('https://example.com');
    
    // 暂停执行（调试用）
    await new Promise(resolve => setTimeout(resolve, 5000));
    
  } finally {
    if (driver) {
      await driver.quit();
    }
  }
}
```

## 总结

本教程基于Steel-Browser项目的实际代码，详细介绍了Selenium WebDriver的使用方法。通过学习本教程，您应该能够：

1. **环境搭建**: 正确安装和配置Selenium WebDriver开发环境
2. **基础操作**: 掌握浏览器启动、页面导航、元素操作等基础功能
3. **高级特性**: 了解等待策略、键盘鼠标操作、多窗口处理等高级功能
4. **最佳实践**: 学会页面对象模式、数据驱动测试、测试框架集成等最佳实践
5. **故障排除**: 掌握常见问题的诊断和解决方法

Selenium WebDriver是一个成熟的浏览器自动化工具，结合Steel-Browser项目的架构，可以构建出功能强大、稳定可靠的Web自动化测试解决方案。