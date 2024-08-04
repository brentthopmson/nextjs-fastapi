import { NextResponse } from "next/server";
import puppeteer, { Browser } from "puppeteer-core";
import chromium from "@sparticuz/chromium-min";
import dns from 'dns';
import { promisify } from 'util';
import { localExecutablePath, isDev, userAgent, remoteExecutablePath } from "@utils/utils";

const resolveMx = promisify(dns.resolveMx);

const platformUrls: Record<string, string> = {
  gmail: "https://accounts.google.com/",
  outlook: "https://login.microsoftonline.com/",
  roundcube: "https://your-roundcube-url.com/",
  aol: "https://login.aol.com/",
};

const platformSelectors: Record<string, { input: string; nextButton: string; errorMessage: string }> = {
  gmail: {
    input: "#identifierId",
    nextButton: "#identifierNext",
    errorMessage: "//*[contains(text(), 'Couldn’t find your Google Account')]",
  },
  outlook: {
    input: "input[name='loginfmt']",
    nextButton: "#idSIButton9",
    errorMessage: "//*[contains(text(), 'This username may be')] | //*[contains(text(), 'That Microsoft account doesn’t exist')] | //*[contains(text(), 'find an account with that')]",
  },
  roundcube: {
    input: "input[name='user']",
    nextButton: "input[name='submitbutton']",
    errorMessage: "//*[contains(text(), 'Login failed')]",
  },
  aol: {
    input: "#login-username",
    nextButton: "#login-signin",
    errorMessage: "//*[contains(text(), 'Sorry, we don’t recognize this email')]",
  },
};

async function checkEmailExists(email: string): Promise<boolean> {
    let browser: Browser | null = null;
    let accountExists = false;
  
    try {
      const domain = email.split('@')[1];
      const mxRecords = await resolveMx(domain);
      if (!mxRecords || mxRecords.length === 0) {
        throw new Error('No MX records found');
      }
  
      const mailServer = mxRecords[0].exchange;
      let platform: keyof typeof platformUrls = '';
  
      if (mailServer.includes('outlook')) {
        platform = 'outlook';
      } else if (mailServer.includes('google') || mailServer.includes('gmail')) {
        platform = 'gmail';
      } else if (mailServer.includes('aol')) {
        platform = 'aol';
      } else if (mailServer.includes('roundcube')) {
        platform = 'roundcube';
      } else {
        throw new Error('Unsupported email service provider');
      }
  
      browser = await puppeteer.launch({
        ignoreDefaultArgs: ["--enable-automation"],
        args: isDev
          ? [
              "--disable-blink-features=AutomationControlled",
              "--disable-features=site-per-process",
              "-disable-site-isolation-trials",
            ]
          : [...chromium.args, "--disable-blink-features=AutomationControlled"],
        defaultViewport: { width: 1920, height: 1080 },
        executablePath: isDev
          ? localExecutablePath
          : await chromium.executablePath(remoteExecutablePath),
        headless: false, // Set to true for production, false for debugging
        debuggingPort: isDev ? 9222 : undefined,
      });
  
      const page = (await browser.pages())[0];
      await page.setUserAgent(userAgent);
      await page.setViewport({ width: 1920, height: 1080 });
  
      await page.goto(platformUrls[platform], { waitUntil: "networkidle2", timeout: 60000 });
  
      const { input, nextButton, errorMessage } = platformSelectors[platform];
  
      await page.waitForSelector(input);
      await page.type(input, email);
      await page.waitForSelector(nextButton);
      await page.click(nextButton);
  
      await new Promise((resolve) => setTimeout(resolve, 4000)); // Wait for the response
  
      const errorElementsCount = await page.evaluate((xpath) => {
        const result = document.evaluate(xpath, document, null, XPathResult.ANY_TYPE, null);
        const nodes: Node[] = [];
        let node;
        while ((node = result.iterateNext())) {
          nodes.push(node);
        }
        return nodes.length;
      }, errorMessage);
  
      accountExists = errorElementsCount === 0;
    } catch (err: unknown) {
      if (err instanceof Error) {
        console.error(`Error checking email: ${err.message}`);
      } else {
        console.error('An unknown error occurred');
      }
    } finally {
      if (browser) {
        await browser.close();
      }
    }
  
    return accountExists;
  }
  

export async function GET(request: Request) {
  const url = new URL(request.url);
  const email = url.searchParams.get("email");

  if (!email) {
    return NextResponse.json({ error: "Missing email parameter" }, { status: 400 });
  }

  const accountExists = await checkEmailExists(email);

  return NextResponse.json({ account_exists: accountExists }, { status: 200 });
}
