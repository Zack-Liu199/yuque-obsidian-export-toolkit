#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FIX_LINKS = ROOT / "scripts" / "fix_yuque_obsidian_links.py"


PATCHES = {
    "dist/lib/sdk.js": [
        (
            """    async getDocs(namespace) {\n        return await this.requestAPI(`repos/${namespace}/docs`);\n    }\n""",
            """    async getDocs(namespace) {\n        const docs = [];\n        let offset = 0;\n        while (true) {\n            const response = await this.request(`repos/${namespace}/docs?offset=${offset}`);\n            const batch = response.data || [];\n            docs.push(...batch);\n            const total = response.meta?.total || docs.length;\n            if (docs.length >= total || batch.length === 0)\n                break;\n            offset += batch.length;\n        }\n        return docs;\n    }\n""",
        ),
    ],
    "dist/lib/crawler.js": [
        (
            "const { host, token, userAgent, clean, metaDir } = config;\nconst sdk = new SDK({ token, host, userAgent });\nconst taskQueue = new PQueue({ concurrency: 10 });\n",
            "function createSDK() {\n    return new SDK({ token: config.token, host: config.host, userAgent: config.userAgent });\n}\nfunction createTaskQueue() {\n    return new PQueue({ concurrency: 10 });\n}\n",
        ),
        (
            "    if (clean)\n        await rm(metaDir);\n",
            "    if (config.clean)\n        await rm(config.metaDir);\n    const sdk = createSDK();\n",
        ),
        (
            "export async function crawlRepo(namespace) {\n    // crawl repo detail/docs/toc\n    logger.success(`Crawling repo detail: ${host}/${namespace}`);\n    const repo = await sdk.getRepoDetail(namespace);\n",
            "export async function crawlRepo(namespace) {\n    const sdk = createSDK();\n    const taskQueue = createTaskQueue();\n    // crawl repo detail/docs/toc\n    logger.success(`Crawling repo detail: ${config.host}/${namespace}`);\n    const repo = await sdk.getRepoDetail(namespace);\n",
        ),
        (
            "            logger.success(` - [${doc.title}](${host}/${namespace}/${doc.slug})`);\n",
            "            logger.success(` - [${doc.title}](${config.host}/${namespace}/${doc.slug})`);\n",
        ),
        (
            "    await writeFile(path.join(metaDir, filePath), content);\n",
            "    await writeFile(path.join(config.metaDir, filePath), content);\n",
        ),
    ],
    "dist/lib/builder.js": [
        (
            "const { outputDir, metaDir } = config;\nconst taskQueue = new PQueue({ concurrency: 10 });\n",
            "",
        ),
        (
            "export async function build() {\n    logger.info('Start building...');\n",
            "export async function build() {\n    logger.info('Start building...');\n    const taskQueue = new PQueue({ concurrency: 10 });\n",
        ),
        (
            "        logger.warn(`No repos found at ${metaDir}`);\n",
            "        logger.warn(`No repos found at ${config.metaDir}`);\n",
        ),
        (
            "        const fullPath = path.join(outputDir, node.filePath);\n",
            "        const fullPath = path.join(config.outputDir, node.filePath);\n",
        ),
        (
            "                    const fullPath = path.join(outputDir, `${doc.filePath}.md`);\n",
            "                    const fullPath = path.join(config.outputDir, `${doc.filePath}.md`);\n",
        ),
        (
            "    const reposPath = await fg('**/repo.json', { cwd: metaDir, deep: 3 });\n",
            "    const reposPath = await fg('**/repo.json', { cwd: config.metaDir, deep: 3 });\n",
        ),
        (
            "        const repoInfo = await readJSON(path.join(metaDir, repoPath));\n",
            "        const repoInfo = await readJSON(path.join(config.metaDir, repoPath));\n",
        ),
    ],
    "dist/lib/tree.js": [
        (
            "const { metaDir } = config;\n",
            "",
        ),
        (
            "    const docs = await readJSON(path.join(metaDir, repo.namespace, 'docs.json'));\n    const toc = await readJSON(path.join(metaDir, repo.namespace, 'toc.json'));\n",
            "    const docs = await readJSON(path.join(config.metaDir, repo.namespace, 'docs.json'));\n    const toc = await readJSON(path.join(config.metaDir, repo.namespace, 'toc.json'));\n",
        ),
    ],
    "dist/lib/doc.js": [
        (
            "const { host, metaDir, outputDir, userAgent } = config;\n",
            "",
        ),
        (
            "    const docDetail = await readJSON(path.join(metaDir, doc.namespace, 'docs', `${doc.url}.json`));\n",
            "    const docDetail = await readJSON(path.join(config.metaDir, doc.namespace, 'docs', `${doc.url}.json`));\n",
        ),
        (
            "        url: `${host}/${doc.namespace}/${doc.url}`,\n",
            "        url: `${config.host}/${doc.namespace}/${doc.url}`,\n",
        ),
        (
            "            if (node.url.startsWith(`${host}/docs/share/`)) {\n                node.url = await getRedirectLink(node.url, host);\n",
            "            if (node.url.startsWith(`${config.host}/docs/share/`)) {\n                node.url = await getRedirectLink(node.url, config.host);\n",
        ),
        (
            "    if (!url.startsWith(host))\n",
            "    if (!url.startsWith(config.host))\n",
        ),
        (
            "    if (url.startsWith(host + '/attachments/'))\n",
            "    if (url.startsWith(config.host + '/attachments/'))\n",
        ),
        (
            "            await download(node.url, path.join(outputDir, filePath), { headers: { 'User-Agent': userAgent } });\n            node.url = path.relative(path.dirname(docFilePath), filePath);\n",
            "            try {\n                await download(node.url, path.join(config.outputDir, filePath), { headers: { 'User-Agent': config.userAgent } });\n                node.url = path.relative(path.dirname(docFilePath), filePath);\n            }\n            catch (error) {\n                console.warn(`[yuque-exporter] skip asset download failed: ${node.url} (${error.message})`);\n            }\n",
        ),
        (
            "            await download(node.url, path.join(config.outputDir, filePath), { headers: { 'User-Agent': config.userAgent } });\n            node.url = path.relative(path.dirname(docFilePath), filePath);\n",
            "            try {\n                await download(node.url, path.join(config.outputDir, filePath), { headers: { 'User-Agent': config.userAgent } });\n                node.url = path.relative(path.dirname(docFilePath), filePath);\n            }\n            catch (error) {\n                console.warn(`[yuque-exporter] skip asset download failed: ${node.url} (${error.message})`);\n            }\n",
        ),
    ],
}

PATCH_CLEANUPS = {
    "dist/lib/builder.js": [
        (
            "    const taskQueue = new PQueue({ concurrency: 10 });\n    const taskQueue = new PQueue({ concurrency: 10 });\n",
            "    const taskQueue = new PQueue({ concurrency: 10 });\n",
        ),
    ],
}


def run(cmd, **kwargs):
    subprocess.run(cmd, check=True, **kwargs)


def ensure_exporter_cache():
    candidates = sorted(Path.home().glob(".npm/_npx/*/node_modules/yuque-exporter"), key=lambda p: p.stat().st_mtime)
    if candidates:
        return
    env = os.environ.copy()
    env["npm_config_registry"] = "https://registry.npmjs.org"
    run(
        ["npx", "-y", "--package", "yuque-exporter", "node", "-e", "require.resolve('yuque-exporter/package.json')"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def find_exporter_dir():
    candidates = sorted(Path.home().glob(".npm/_npx/*/node_modules/yuque-exporter"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise SystemExit("yuque-exporter cache not found after npx bootstrap")
    return candidates[-1]


def apply_patches(exporter_dir: Path):
    for rel_path, replacements in PATCHES.items():
        file_path = exporter_dir / rel_path
        content = file_path.read_text()
        updated = content
        for old, new in replacements:
            if new and new in updated:
                continue
            if old in updated:
                updated = updated.replace(old, new)
        for old, new in PATCH_CLEANUPS.get(rel_path, []):
            while old in updated:
                updated = updated.replace(old, new)
        if updated != content:
            file_path.write_text(updated)


def flatten_vault(vault_dir: Path):
    inner = vault_dir / vault_dir.name
    if not inner.is_dir():
        return
    for child in inner.iterdir():
        shutil.move(str(child), str(vault_dir / child.name))
    inner.rmdir()


def main():
    parser = argparse.ArgumentParser(description="Export one or more Yuque repos to an Obsidian-friendly vault")
    parser.add_argument("namespaces", nargs="+", help="repo namespaces, e.g. shiwozack/mywife shiwozack/findjob")
    parser.add_argument("output_dir", help="target vault directory")
    parser.add_argument("--token", default=os.environ.get("YUQUE_TOKEN"), help="Yuque access token")
    parser.add_argument("--host", default="https://www.yuque.com", help="Yuque host")
    args = parser.parse_args()
    if not args.token:
        parser.error("--token is required (or set YUQUE_TOKEN)")

    ensure_exporter_cache()
    exporter_dir = find_exporter_dir()
    apply_patches(exporter_dir)

    output_dir = Path(args.output_dir).resolve()
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    run(
        [
            "node",
            str(exporter_dir / "dist/bin/cli.js"),
            "--clean",
            f"--token={args.token}",
            f"--outputDir={output_dir}",
            f"--host={args.host}",
            *args.namespaces,
        ],
        cwd=ROOT,
    )

    flatten_vault(output_dir)
    run(["python3", str(FIX_LINKS), str(output_dir)], cwd=ROOT)


if __name__ == "__main__":
    main()
