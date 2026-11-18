import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import { compileAsync } from "sass";

const root = path.dirname(fileURLToPath(import.meta.url));
const staticDir = path.resolve(root, "app/static");
const tnaAssets = path.resolve(
  root,
  "node_modules/@nationalarchives/frontend/nationalarchives/assets",
);

function copyDirectory(source, destination) {
  if (!fs.existsSync(source)) {
    throw new Error(`Required asset directory is missing: ${source}`);
  }
  fs.mkdirSync(destination, { recursive: true });
  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    const from = path.join(source, entry.name);
    const to = path.join(destination, entry.name);
    if (entry.isDirectory()) {
      copyDirectory(from, to);
    } else {
      fs.copyFileSync(from, to);
    }
  }
}

/**
 * TNA Frontend references its webfonts and icons at stable paths. Copy them
 * outside of the Rollup graph so the compiled CSS can use relative asset URLs
 * under the configured public static path without hash rewriting.
 */
function copyTnaAssets() {
  return {
    name: "copy-tna-assets",
    apply: "build",
    closeBundle() {
      copyDirectory(
        path.join(tnaAssets, "fonts"),
        path.join(staticDir, "assets/fonts"),
      );
      copyDirectory(
        path.join(tnaAssets, "images"),
        path.join(staticDir, "assets/images"),
      );
    },
  };
}

function compileStyles() {
  return {
    name: "compile-styles",
    apply: "build",
    async buildStart() {
      const stylesDir = path.resolve(root, "src/styles");
      const entries = fs
        .readdirSync(stylesDir, { withFileTypes: true })
        .filter(
          (entry) =>
            entry.isFile() &&
            entry.name.endsWith(".scss") &&
            !entry.name.startsWith("_"),
        )
        .map((entry) => entry.name)
        .sort();

      for (const entry of entries) {
        const name = path.basename(entry, ".scss");
        const cssFile = `${name}.css`;
        const mapFile = `${cssFile}.map`;
        const result = await compileAsync(path.join(stylesDir, entry), {
          loadPaths: [path.resolve(root, "node_modules")],
          style: "compressed",
          sourceMap: true,
          sourceMapIncludeSources: true,
        });
        for (const url of result.loadedUrls) {
          if (url.protocol === "file:") {
            this.addWatchFile(fileURLToPath(url));
          }
        }
        this.emitFile({
          type: "asset",
          fileName: cssFile,
          source: `${result.css}\n/*# sourceMappingURL=${mapFile} */\n`,
        });
        this.emitFile({
          type: "asset",
          fileName: mapFile,
          source: JSON.stringify({
            ...result.sourceMap,
            file: cssFile,
            sources: result.sourceMap.sources.map((source) =>
              path
                .relative(staticDir, fileURLToPath(source))
                .split(path.sep)
                .join("/"),
            ),
          }),
        });
      }
    },
  };
}

export default defineConfig({
  root,
  publicDir: false,
  build: {
    outDir: staticDir,
    emptyOutDir: false,
    sourcemap: true,
    rollupOptions: {
      input: {
        main: path.resolve(root, "src/scripts/main.js"),
        analytics: path.resolve(root, "src/scripts/analytics.js"),
      },
      output: {
        format: "es",
        entryFileNames: "[name].min.js",
        chunkFileNames: "[name].min.js",
        assetFileNames: "[name][extname]",
      },
    },
  },
  plugins: [compileStyles(), copyTnaAssets()],
});
