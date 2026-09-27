import {build} from 'esbuild';
import {copyFile, readFile, appendFile} from 'node:fs/promises';
await build({entryPoints:['src/main.jsx'], bundle:true, minify:true, format:'iife', jsx:'automatic',
  define:{'process.env.NODE_ENV':'"production"'}, outfile:'../vesper/assets/workspace.js', legalComments:'external'});
await copyFile('src/workspace.css','../vesper/assets/workspace.css');

for (const name of ['react','react-dom','scheduler']) {
  const license=await readFile(`node_modules/${name}/LICENSE`, 'utf8');
  await appendFile('../vesper/assets/workspace.js.LEGAL.txt', `

${name} — full license
${license}`);
}
