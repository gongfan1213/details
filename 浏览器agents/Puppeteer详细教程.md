# Puppeteer详细教程 - 基于Steel-Browser项目实战

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
mkdir puppeteer-project
cd puppeteer-project

# 初始化Node.js项目
npm init -y

# 安装Puppeteer核心依赖
npm install puppeteer-core
npm install puppeteer

# 安装TypeScript和开发工具
npm install -D typescript @types/node ts-node
npm install -D nodemon

# 创建TypeScript配置文件
npx tsc --init
```

### 2. 环境配置

```bash
# 创建.env文件配置环境变量
cat > .env << EOF
CHROME_EXECUTABLE_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
CHROME_HEADLESS=false
CHROME_ARGS="--no-sandbox,--disable-dev-shm-usage"
EOF
```

### 3. 验证安装

```typescript
import puppeteer from 'puppeteer';

async function testPuppeteerInstallation() {
  console.log('🚀 测试Puppeteer安装...');
  
  try {
    const browser = await puppeteer.launch({
      headless: false,
      args: ['--no-sandbox', '--disable-dev-shm-usage']
    });
    
    const page = await browser.newPage();
    await page.goto('https://example.com');
    
    const title = await page.title();
    console.log(`页面标题: ${title}`);
    
    await browser.close();
    console.log('✅ Puppeteer安装成功！');
  } catch (error) {
    console.error('❌ Puppeteer安装失败:', error);
  }
}

testPuppeteerInstallation().catch(console.error);
```

## 基础概念

### 1. Puppeteer核心组件

#### Browser（浏览器）
- **Puppeteer**: 完整的浏览器自动化库
- **Puppeteer-Core**: 轻量级版本，需要手动管理浏览器

#### BrowserContext（浏览器上下文）
- 独立的浏览器会话
- 支持多标签页
- 可配置用户代理、视口等

#### Page（页面）
- 单个标签页
- 主要的交互对象
- 包含DOM操作、网络请求等功能

### 2. Steel-Browser架构概览

```
Steel-Browser API
├── CDPService (CDP服务)
│   ├── Browser Instance (浏览器实例)
│   ├── Plugin Manager (插件管理器)
│   └── Fingerprint Injector (指纹注入器)
├── SessionService (会话服务)
│   ├── Browser Launcher (浏览器启动器)
│   └── Context Manager (上下文管理器)
└── SeleniumService (Selenium服务)
    ├── Selenium Server (Selenium服务器)
    └── WebDriver Protocol (WebDriver协议)
```

## 核心架构

### 1. CDPService类详解

基于 `steel-browser/api/src/services/cdp/cdp.service.ts`：

```typescript
import puppeteer, {
  Browser,
  BrowserContext,
  CDPSession,
  HTTPRequest,
  Page,
  Protocol,
  Target,
  TargetType,
} from "puppeteer-core";

export class CDPService extends EventEmitter {
  private browserInstance: Browser | null;
  private wsEndpoint: string | null;
  private fingerprintData: BrowserFingerprintWithHeaders | null;
  private chromeExecPath: string;
  private primaryPage: Page | null;
  private pluginManager: PluginManager;

  constructor(config: { keepAlive?: boolean }, logger: FastifyBaseLogger) {
    super();
    this.logger = logger;
    this.keepAlive = config.keepAlive ?? false;
    this.browserInstance = null;
    this.wsEndpoint = null;
    this.fingerprintData = null;
    this.chromeExecPath = getChromeExecutablePath();
    this.primaryPage = null;
    this.pluginManager = new PluginManager();
  }

  @traceable
  private async launchInternal(config?: BrowserLauncherOptions): Promise<Browser> {
    const launchTimeout = new Promise<never>((_, reject) => {
      setTimeout(() => {
        reject(new LaunchTimeoutError("Browser launch timeout"));
      }, 30000);
    });

    const launchProcess = (async () => {
      const shouldReuseInstance = this.browserInstance && this.keepAlive;
      
      if (shouldReuseInstance) {
        return this.browserInstance;
      }

      const options = config?.options ?? {};
      const timezone = await this.getTimezone(config);
      const userDataDir = await this.getUserDataDir(config);

      const launchArgs = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-web-security",
        "--disable-site-isolation-trials",
        "--disable-features=IsolateOrigins,site-per-process",
        ...env.CHROME_ARGS,
      ].filter(Boolean).filter((arg) => !env.FILTER_CHROME_ARGS.includes(arg));

      const finalLaunchOptions = {
        ...options,
        defaultViewport: null,
        args: launchArgs,
        executablePath: this.chromeExecPath,
        timeout: 0,
        env: {
          TZ: timezone,
        },
        userDataDir,
        dumpio: env.DEBUG_CHROME_PROCESS,
      };

      // Browser process launch - most critical step
      try {
        this.browserInstance = await tracer.startActiveSpan(
          "CDPService.launchBrowser",
          async () => {
            return await puppeteer.launch(finalLaunchOptions);
          },
        ) as unknown as Browser;
      } catch (error) {
        throw new BrowserProcessError(
          error instanceof Error ? error.message : String(error),
          BrowserProcessState.LAUNCH_FAILED,
        );
      }

      return this.browserInstance;
    })();

    return Promise.race([launchProcess, launchTimeout]);
  }
}
```

### 2. 浏览器连接示例

基于 `steel-browser/repl/src/script.ts`：

```typescript
import puppeteer from "puppeteer-core";

async function connectToSteelBrowser() {
  // WebSocket endpoint to connect Browser using Chrome DevTools Protocol (CDP)
  const wsEndpoint = "ws://0.0.0.0:3000";
  const browser = await puppeteer.connect({ browserWSEndpoint: wsEndpoint });
  
  try {
    const page = await browser.newPage();

    // Navigate to a website and log the title
    await page.goto("https://steel.dev");
    console.log(`Page title: ${await page.title()}`);
    
    // 执行一些自动化操作
    await page.type('input[type="text"]', '搜索内容');
    await page.click('button[type="submit"]');
    
    // 等待页面加载
    await page.waitForSelector('.search-results');
    
    // 获取搜索结果
    const results = await page.$$eval('.search-result', elements => 
      elements.map(el => el.textContent)
    );
    
    console.log('搜索结果:', results);
    
  } finally {
    // Cleanup: close all pages and disconnect browser
    await Promise.all((await browser.pages()).map((p) => p.close()));
    await browser.disconnect();  
  }
}

connectToSteelBrowser().catch(console.error);
```
