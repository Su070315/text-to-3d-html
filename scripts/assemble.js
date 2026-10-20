// 通用组装脚本: 把 templates 里的库 + 你的 app.js 拼成单个离线 HTML
// 用法: node assemble.js <app.js> <输出.html>
const fs = require('fs');
const path = require('path');
const DIR = __dirname;
const TPL = path.join(DIR, '..', 'templates');
const args = process.argv.slice(2);
const appJs = args[0] || path.join(TPL, 'manor_app.js');
const outHtml = args[1] || path.join(require('os').homedir(), 'Desktop', 'model.html');
const parts = [
  fs.readFileSync(path.join(TPL, 'shell.html'), 'utf8'),
  fs.readFileSync(path.join(TPL, 'three.min.js'), 'utf8'),
  '\n</script>\n<script>\n',
  fs.readFileSync(path.join(TPL, 'OrbitControls.js'), 'utf8'),
  '\n</script>\n<script>\n',
  fs.readFileSync(path.join(TPL, 'GLTFExporter.js'), 'utf8'),
  '\n</script>\n<script>\n',
  fs.readFileSync(appJs, 'utf8'),
  '\n</script>\n</body>\n</html>'
];
fs.writeFileSync(outHtml, parts.join(''));
console.log('ASSEMBLED', outHtml, fs.statSync(outHtml).size, 'bytes');
