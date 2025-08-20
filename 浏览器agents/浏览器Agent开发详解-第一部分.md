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

### 1. 创建Node.js项目

```bash
# 创建项目目录
mkdir puppeteer-project
cd puppeteer-project

# 初始化package.json
npm init -y

# 安装Puppeteer核心依赖
npm install puppeteer-core
npm install puppeteer

# 安装TypeScript相关依赖
npm install -D typescript @types/node ts-node

# 安装开发工具
npm install -D nodemon
```

### 2. 配置TypeScript

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### 3. 环境配置

```bash
# 创建.env文件
cat > .env << EOF
NODE_ENV=development
HOST=0.0.0.0
PORT=3000
CHROME_EXECUTABLE_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
CHROME_HEADLESS=false
DEBUG_CHROME_PROCESS=false
EOF
```

### 4. 验证安装

```typescript
// src/test-installation.ts
import puppeteer from 'puppeteer';

async function testPuppeteerInstallation() {
  console.log('🚀 测试Puppeteer安装...');
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.goto('https://example.com');
  
  const title = await page.title();
  console.log(`✅ 页面标题: ${title}`);
  
  await browser.close();
  console.log('✅ Puppeteer安装成功！');
}

testPuppeteerInstallation().catch(console.error);
```

## 基础概念

### 1. Puppeteer核心组件

#### Browser（浏览器）
- **Puppeteer**: 完整的浏览器自动化库
- **Puppeteer-Core**: 轻量级版本，需要手动管理浏览器
- **Chrome DevTools Protocol (CDP)**: 底层通信协议

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
├── SessionService (会话服务)
├── SeleniumService (Selenium服务)
├── Browser Context (浏览器上下文)
│   ├── Page (页面)
│   ├── CDP Session (CDP会话)
│   └── Event Bus (事件总线)
└── Plugin System (插件系统)
```

## 核心架构

### 1. CDPService类详解

```typescript
// 基于 steel-browser/api/src/services/cdp/cdp.service.ts

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
  private logger: FastifyBaseLogger;
  private browserInstance: Browser | null = null;
  private chromeExecPath: string;

  constructor(logger: FastifyBaseLogger) {
    super();
    this.logger = logger;
    this.chromeExecPath = getChromeExecutablePath();
  }

  @traceable
  private async launchInternal(config?: BrowserLauncherOptions): Promise<Browser> {
    const launchTimeout = new Promise((_, reject) => {
      setTimeout(() => {
        reject(new LaunchTimeoutError("Browser launch timeout"));
      }, 30000);
    });

    const launchProcess = (async () => {
      const shouldReuseInstance = this.browserInstance;
      
      const launchArgs = [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        ...env.CHROME_ARGS,
      ].filter(Boolean);

      const finalLaunchOptions = {
        headless: env.CHROME_HEADLESS,
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

      this.logger.info(`[CDPService] Launch Options:`, JSON.stringify(finalLaunchOptions, null, 2));

      // 启动浏览器进程
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

      // 设置浏览器事件监听
      this.browserInstance.on("error", (error) => {
        this.logger.error(`[CDPService] Browser error: ${error}`);
        this.emit("browserError", error);
      });

      this.browserInstance.on("disconnected", () => {
        this.logger.info(`[CDPService] Browser disconnected`);
        this.browserInstance = null;
        this.emit("browserDisconnected");
      });

      return this.browserInstance;
    })();

    return Promise.race([launchProcess, launchTimeout]) as Promise<Browser>;
  }

  public async createBrowserContext(proxyUrl?: string): Promise<BrowserContext> {
    if (!this.browserInstance) {
      throw new Error("Browser not launched");
    }

    const contextOptions: any = {
      viewport: null,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
      javaScriptEnabled: true,
      bypassCSP: true,
      ignoreHTTPSErrors: true,
    };

    if (proxyUrl) {
      contextOptions.proxy = proxyUrl;
    }

    return await this.browserInstance.createIncognitoBrowserContext(contextOptions);
  }

  public async getPrimaryPage(): Promise<Page> {
    if (!this.browserInstance) {
      throw new Error("Browser not launched");
    }

    const pages = await this.browserInstance.pages();
    if (pages.length === 0) {
      return await this.browserInstance.newPage();
    }
    return pages[0];
  }
}
```

### 2. SessionService类详解

```typescript
// 基于 steel-browser/api/src/services/session.service.ts

export class SessionService {
  private logger: FastifyBaseLogger;
  private cdpService: CDPService;
  private seleniumService: SeleniumService;
  private activeSession: SessionDetails;

  constructor(logger: FastifyBaseLogger) {
    this.logger = logger;
    this.cdpService = new CDPService(logger);
    this.seleniumService = new SeleniumService(logger);
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
      blockAds = false,
      extensions = [],
      timezone,
      dimensions,
      extra,
      credentials,
      skipFingerprintInjection = false,
      userPreferences,
    } = options;

    // 设置会话ID
    this.activeSession.id = sessionId || uuid7str();

    // 创建代理服务器（如果需要）
    if (proxyUrl) {
      this.activeSession.proxyServer = await this.proxyFactory(proxyUrl);
      await this.activeSession.proxyServer.listen();
    }

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
      extensions,
      logSinkUrl,
      timezone,
      dimensions,
      userDataDir,
      userPreferences: mergedUserPreferences,
      extra,
      credentials,
      skipFingerprintInjection,
    };

    if (isSelenium) {
      // 启动Selenium服务
      await this.cdpService.shutdown();
      await this.seleniumService.launch(browserLauncherOptions);

      Object.assign(this.activeSession, {
        websocketUrl: "",
        debugUrl: "",
        sessionViewerUrl: "",
        userAgent: userAgent || "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
      });
    } else {
      // 启动CDP服务
      await this.cdpService.startNewSession(browserLauncherOptions);

      Object.assign(this.activeSession, {
        websocketUrl: getBaseUrl("ws"),
        debugUrl: getUrl("v1/sessions/debug"),
        debuggerUrl: getUrl("v1/devtools/inspector.html"),
        sessionViewerUrl: getBaseUrl(),
        userAgent: this.cdpService.getUserAgent() || "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
      });
    }

    return this.activeSession;
  }
}
```

## 实战示例

### 1. 基础浏览器自动化

```typescript
// src/examples/basic-automation.ts
import puppeteer from 'puppeteer';

async function basicAutomation() {
  console.log('🚀 开始基础浏览器自动化...');
  
  const browser = await puppeteer.launch({
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // 设置视口
    await page.setViewport({ width: 1200, height: 800 });
    
    // 导航到网站
    console.log('📱 导航到百度...');
    await page.goto('https://www.baidu.com', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    
    // 等待搜索框加载
    await page.waitForSelector('#kw', { timeout: 10000 });
    
    // 输入搜索关键词
    console.log('🔍 搜索"Puppeteer教程"...');
    await page.type('#kw', 'Puppeteer教程');
    
    // 点击搜索按钮
    await page.click('#su');
    
    // 等待搜索结果加载
    await page.waitForSelector('.result', { timeout: 10000 });
    
    // 获取搜索结果
    const results = await page.evaluate(() => {
      const resultElements = document.querySelectorAll('.result h3 a');
      return Array.from(resultElements).map(el => ({
        title: el.textContent?.trim(),
        url: el.getAttribute('href')
      })).slice(0, 5);
    });
    
    console.log('📋 搜索结果:');
    results.forEach((result, index) => {
      console.log(`${index + 1}. ${result.title}`);
      console.log(`   URL: ${result.url}`);
    });
    
    // 截图
    await page.screenshot({ 
      path: 'search-results.png',
      fullPage: true 
    });
    console.log('📸 截图已保存为 search-results.png');
    
  } catch (error) {
    console.error('❌ 自动化过程中出现错误:', error);
  } finally {
    await browser.close();
    console.log('✅ 浏览器已关闭');
  }
}

basicAutomation().catch(console.error);
```

### 2. 表单填写自动化

```typescript
// src/examples/form-filling.ts
import puppeteer from 'puppeteer';

async function formFilling() {
  console.log('🚀 开始表单填写自动化...');
  
  const browser = await puppeteer.launch({
    headless: false,
    ar