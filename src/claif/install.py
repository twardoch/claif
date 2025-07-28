# this_file: claif/src/claif/install.py

import shutil
import subprocess
from pathlib import Path

from loguru import logger

from claif.common.utils import get_claif_bin_path


def ensure_bun_installed() -> bool:
    """Ensure bun is installed. Install if not present."""
    bun_path = Path.home() / ".bun" / "bin" / "bun"

    if bun_path.exists() and bun_path.is_file():
        logger.debug(f"bun found at {bun_path}")
        return True

    logger.info("bun not found. Installing bun...")
    try:
        # Install bun using the official installer
        subprocess.run(["curl", "-fsSL", "https://bun.sh/install"], stdout=subprocess.PIPE, check=True)

        # Run the installer
        subprocess.run(
            ["bash", "-c", "curl -fsSL https://bun.sh/install | bash"], capture_output=True, text=True, check=True
        )

        if bun_path.exists():
            logger.success("✓ bun installed successfully")
            return True
        logger.error("bun installation failed - executable not found")
        return False

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install bun: {e}")
        return False


def get_install_location() -> Path:
    """Get the claif-owned install location for bundled executables."""
    install_dir = get_claif_bin_path()

    # Create directory if it doesn't exist
    install_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Using claif install directory: {install_dir}")
    return install_dir


def install_npm_package_globally(package: str) -> bool:
    """Install an npm package globally using bun."""
    bun_path = Path.home() / ".bun" / "bin" / "bun"

    if not bun_path.exists():
        logger.error("bun not found")
        return False

    try:
        logger.info(f"Installing {package}...")
        subprocess.run([str(bun_path), "add", "-g", package], capture_output=True, text=True, check=True)

        logger.success(f"✓ {package} installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package}: {e.stderr}")
        return False


def get_bundle_script_path() -> Path | None:
    """Get the path to the bundle-optimized.sh script."""
    # Get the claif-packages root directory (from claif/src/claif/install.py)
    claif_packages_root = Path(__file__).parent.parent.parent.parent
    bundle_script = claif_packages_root / "bundle" / "bundle-optimized.sh"

    if bundle_script.exists():
        return bundle_script

    logger.error(f"Bundle script not found: {bundle_script}")
    return None


def bundle_all_tools() -> Path | None:
    """Bundle all CLI tools using the optimized script."""
    bundle_script = get_bundle_script_path()
    if not bundle_script:
        return None

    try:
        logger.info("Bundling CLI tools...")
        subprocess.run(
            ["bash", str(bundle_script)], cwd=bundle_script.parent, capture_output=True, text=True, check=True
        )

        # Return the dist directory if successful
        dist_dir = bundle_script.parent / "dist"
        if dist_dir.exists():
            logger.success("✓ All tools bundled successfully")
            return dist_dir
        logger.error("Bundling completed but dist directory not found")
        return None

    except subprocess.CalledProcessError as e:
        logger.error(f"Bundling failed: {e.stderr}")
        return None


def install_portable_tool(tool_name: str, install_dir: Path, dist_dir: Path) -> bool:
    """Install a portable bundled tool (Gemini or Codex)."""
    try:
        tool_source = dist_dir / tool_name / tool_name
        if not tool_source.exists():
            logger.error(f"Bundled {tool_name} not found at {tool_source}")
            return False

        # Copy the executable directly
        tool_target = install_dir / tool_name
        shutil.copy2(tool_source, tool_target)
        tool_target.chmod(0o755)

        logger.success(f"✓ {tool_name} installed at {tool_target}")
        return True

    except Exception as e:
        logger.error(f"Failed to install {tool_name}: {e}")
        return False


def uninstall_tool(tool_name: str, install_dir: Path | None = None) -> bool:
    """Uninstall a tool (remove executable and directory if exists)."""
    if install_dir is None:
        install_dir = get_install_location()

    try:
        # Remove wrapper script/executable
        tool_path = install_dir / tool_name
        if tool_path.exists():
            if tool_path.is_file():
                tool_path.unlink()
                logger.info(f"Removed executable: {tool_path}")

        # Remove installation directory (for Claude, use claude-bin)
        tool_dir = install_dir / "claude-bin" if tool_name == "claude" else install_dir / tool_name

        if tool_dir.exists() and tool_dir.is_dir():
            shutil.rmtree(tool_dir)
            logger.info(f"Removed directory: {tool_dir}")

        logger.success(f"✓ {tool_name} uninstalled")
        return True

    except Exception as e:
        logger.error(f"Failed to uninstall {tool_name}: {e}")
        return False


def install_all_tools() -> dict:
    """Install all tools (claude, gemini, codex)."""
    tools = ["claude", "gemini", "codex"]
    packages = {"claude": "@anthropic-ai/claude-code", "gemini": "@google/gemini-cli", "codex": "@openai/codex"}

    if not ensure_bun_installed():
        return {"installed": [], "failed": tools, "message": "bun installation failed"}

    install_dir = get_install_location()
    results = {"installed": [], "failed": []}

    # Install npm packages globally first
    logger.info("Installing npm packages...")
    for tool in tools:
        if not install_npm_package_globally(packages[tool]):
            results["failed"].append(tool)

    # Bundle all tools
    dist_dir = bundle_all_tools()
    if not dist_dir:
        failed_tools = [t for t in tools if t not in results["failed"]]
        results["failed"].extend(failed_tools)
        return results

    # Install each tool
    for tool in tools:
        if tool in results["failed"]:
            continue

        logger.info(f"Installing {tool}...")
        if tool == "claude":
            # Import and use Claude-specific installer
            from claif_cla.install import install_claude_bundled

            success = install_claude_bundled(install_dir, dist_dir)
        elif tool == "gemini":
            # Import and use Gemini-specific installer
            from claif_gem.install import install_gemini_bundled

            success = install_gemini_bundled(install_dir, dist_dir)
        elif tool == "codex":
            # Import and use Codex-specific installer
            from claif_cod.install import install_codex

            result = install_codex()
            success = bool(result.get("installed"))
        else:
            success = install_portable_tool(tool, install_dir, dist_dir)

        if success:
            results["installed"].append(tool)
        else:
            results["failed"].append(tool)

    return results


def uninstall_all_tools() -> dict:
    """Uninstall all tools."""
    tools = ["claude", "gemini", "codex"]
    install_dir = get_install_location()
    results = {"uninstalled": [], "failed": []}

    for tool in tools:
        if uninstall_tool(tool, install_dir):
            results["uninstalled"].append(tool)
        else:
            results["failed"].append(tool)

    return results
