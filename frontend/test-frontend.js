const { chromium } = require('playwright');

(async () => {
  console.log('🚀 Starting frontend tests with Playwright...');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  console.log('📡 Navigating to http://localhost:8000 ...');
  await page.goto('http://localhost:8000');
  
  // Проверяем заголовок страницы
  const title = await page.title();
  console.log(`   Page title: ${title}`);
  
  // Проверяем наличие формы регистрации
  const hasAuthForm = await page.locator('.auth-container').count();
  console.log(`   Auth container found: ${hasAuthForm > 0}`);
  
  if (hasAuthForm > 0) {
    console.log('📝 Testing registration...');
    
    // Заполняем форму регистрации
    await page.fill('#username', 'playwright-test');
    await page.fill('#email', 'playwright@test.com');
    await page.fill('#password', 'test123456');
    
    // Нажимаем кнопку регистрации
    await page.click('button[type="submit"]');
    
    // Ждём ответа от сервера (2 секунды)
    await page.waitForTimeout(2000);
    
    // Проверяем, что ошибка не появилась
    const errorEl = await page.locator('#auth-error');
    const isHidden = await errorEl.isHidden();
    console.log(`   Error visible: ${!isHidden}`);
    
    if (!isHidden) {
      const errorText = await errorEl.textContent();
      console.log(`   Error text: ${errorText}`);
    }
    
    // Проверяем URL после регистрации (должен остаться на той же странице или перейти)
    const currentUrl = page.url();
    console.log(`   Current URL: ${currentUrl}`);
    
    // Проверяем, что есть кнопка выхода (признак успешного входа)
    const hasLogout = await page.locator('button:has-text("Выйти")').count();
    console.log(`   Logout button found: ${hasLogout > 0}`);
    
    if (hasLogout > 0) {
      console.log('✅ Registration and login successful!');
    } else {
      console.log('⚠️ Registration may have failed.');
    }
  }
  
  await browser.close();
  console.log('✅ Frontend tests completed!');
})().catch(e => {
  console.error('❌ Frontend test failed:', e);
  process.exit(1);
});
