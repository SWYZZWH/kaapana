const fs = require('fs');
const path = require('path');

const pngToIco = async (pngPath, icoPath) => {
  try {
    const toIco = require('to-ico');
    const png = fs.readFileSync(pngPath);
    const buf = await toIco(png);
    fs.writeFileSync(icoPath, buf);
    console.log(`Generated ${icoPath}`);
  } catch (err) {
    console.warn('to-ico missing or conversion failed, falling back to copying favicon.ico if present.', err.message);
    const fallback = path.resolve(__dirname, '../public/favicon.ico');
    if (fs.existsSync(fallback)) {
      fs.copyFileSync(fallback, icoPath);
      console.log(`Copied fallback favicon.ico to ${icoPath}`);
    } else {
      console.warn('No fallback favicon.ico found. Skipping ico generation.');
    }
  }
};

(async () => {
  const projectRoot = path.resolve(__dirname, '..');
  const pngPath = path.join(projectRoot, 'src/assets/img/logo.png');
  const icoPath = path.join(projectRoot, 'public/logo.ico');
  await pngToIco(pngPath, icoPath);
})();


