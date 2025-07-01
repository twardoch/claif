#!/usr/bin/env python3
# this_file: claif/src/claif/common/install.py
"""Shared installation utilities for CLAIF packages."""

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class InstallError(Exception):
    """Exception raised during installation."""


def get_install_dir() -> Path:
    """Get the directory where bundled executables should be installed."""
    # Use ~/.local/bin on Unix-like systems, %LOCALAPPDATA%\Programs on Windows
    if platform.system() == "Windows":
        return Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "claif"
    else:
        return Path.home() / ".local" / "bin"


def ensure_install_dir() -> Path:
    """Ensure the install directory exists and return it."""
    install_dir = get_install_dir()
    install_dir.mkdir(parents=True, exist_ok=True)
    return install_dir


def check_bun_available() -> bool:
    """Check if bun is available in PATH."""
    return shutil.which("bun") is not None


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
        result = subprocess.run(
            ["bash", "-c", "curl -fsSL https://bun.sh/install | bash"], capture_output=True, text=True, check=True
        )

        if bun_path.exists():
            logger.success("✓ bun installed successfully")
            return True
        else:
            logger.error("bun installation failed - executable not found")
            return False

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install bun: {e}")
        return False


def get_install_location() -> Path:
    """Get the priority install location for executables."""
    # Check common priority PATH locations
    locations = [
        Path.home() / ".local" / "bin",
        Path("/usr/local/bin"),
        Path.home() / "bin",
    ]

    for location in locations:
        if location.exists() and os.access(location, os.W_OK):
            return location

    # Create ~/.local/bin if none exist
    local_bin = Path.home() / ".local" / "bin"
    local_bin.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created install directory: {local_bin}")
    return local_bin


def install_npm_package(package: str) -> bool:
    """Install the latest version of an npm package using bun.

    Args:
        package: npm package name (e.g., '@anthropic-ai/claude-code')

    Returns:
        True if installation succeeded, False otherwise.
    """
    if not check_bun_available():
        if not ensure_bun_installed():
            return False

    console.print(f"[bold]Installing {package}...[/bold]")

    try:
        # Use bun to install the latest version globally
        bun_path = shutil.which("bun") or str(Path.home() / ".bun" / "bin" / "bun")
        subprocess.run([bun_path, "add", "-g", package], check=True)
        console.print(f"[green]✓ {package} installed successfully[/green]")
        return True

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to install {package}: {e}[/red]")
        return False


def install_npm_package_with_bun(package: str) -> bool:
    """Install an npm package globally using bun."""
    bun_path = Path.home() / ".bun" / "bin" / "bun"

    if not bun_path.exists():
        logger.error("bun not found")
        return False

    try:
        logger.info(f"Installing {package}...")
        result = subprocess.run([str(bun_path), "add", "-g", package], capture_output=True, text=True, check=True)

        logger.success(f"✓ {package} installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package}: {e.stderr}")
        return False


def bundle_executable(provider: str, exec_name: str) -> bool:
    """Bundle a provider executable using the bundle script.

    Args:
        provider: Provider name (claude, gemini, codex)
        exec_name: Name of the executable to create

    Returns:
        True if bundling succeeded, False otherwise.
    """
    # Find the bundle script
    bundle_script = None

    # Look for bundle script relative to this file
    current_dir = Path(__file__).parent
    for search_dir in [current_dir.parent.parent.parent.parent / "bundle", Path.cwd() / "bundle"]:
        script_path = search_dir / "bundle.sh"
        if script_path.exists():
            bundle_script = script_path
            break

    if not bundle_script:
        console.print("[red]Bundle script not found[/red]")
        return False

    console.print(f"[bold]Bundling {provider} executable...[/bold]")

    try:
        # Run the bundle script
        result = subprocess.run(["bash", str(bundle_script)], cwd=bundle_script.parent, capture_output=True, text=True)

        if result.returncode == 0:
            # Check if the executable was created
            bundle_dir = bundle_script.parent
            exec_path = bundle_dir / exec_name

            if exec_path.exists():
                console.print(f"[green]✓ {provider} bundled successfully[/green]")
                return True
            else:
                console.print(f"[red]Bundling succeeded but {exec_name} not found[/red]")
                return False
        else:
            console.print(f"[red]Bundling failed: {result.stderr}[/red]")
            return False

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to bundle {provider}: {e}[/red]")
        return False


def install_bundled_executable(provider: str, exec_name: str) -> bool:
    """Install a bundled executable to the install directory.

    Args:
        provider: Provider name (claude, gemini, codex)
        exec_name: Name of the executable

    Returns:
        True if installation succeeded, False otherwise.
    """
    # Find the bundled executable
    bundle_dir = None
    current_dir = Path(__file__).parent

    for search_dir in [current_dir.parent.parent.parent.parent / "bundle", Path.cwd() / "bundle"]:
        if search_dir.exists():
            bundle_dir = search_dir
            break

    if not bundle_dir:
        console.print("[red]Bundle directory not found[/red]")
        return False

    exec_path = bundle_dir / exec_name
    if not exec_path.exists():
        console.print(f"[red]Bundled executable {exec_name} not found[/red]")
        return False

    # Install to the install directory
    install_dir = ensure_install_dir()
    target_path = install_dir / exec_name

    try:
        # Copy the executable
        shutil.copy2(exec_path, target_path)

        # Make it executable on Unix-like systems
        if platform.system() != "Windows":
            target_path.chmod(0o755)

        # Copy any additional files (like yoga.wasm for Claude)
        for additional_file in bundle_dir.glob(f"{exec_name}.*"):
            if additional_file != exec_path:
                shutil.copy2(additional_file, install_dir / additional_file.name)

        console.print(f"[green]✓ {exec_name} installed to {target_path}[/green]")

        # Check if install dir is in PATH
        if str(install_dir) not in os.environ.get("PATH", ""):
            console.print(f"[yellow]⚠ Add {install_dir} to your PATH to use {exec_name} globally[/yellow]")

        return True

    except Exception as e:
        console.print(f"[red]Failed to install {exec_name}: {e}[/red]")
        return False


def uninstall_bundled_executable(exec_name: str) -> bool:
    """Remove a bundled executable from the install directory.

    Args:
        exec_name: Name of the executable to remove

    Returns:
        True if removal succeeded, False otherwise.
    """
    install_dir = get_install_dir()
    exec_path = install_dir / exec_name

    if not exec_path.exists():
        console.print(f"[yellow]{exec_name} not found in {install_dir}[/yellow]")
        return True  # Not an error if it's already gone

    try:
        # Remove the executable
        exec_path.unlink()

        # Remove any additional files
        for additional_file in install_dir.glob(f"{exec_name}.*"):
            additional_file.unlink()

        console.print(f"[green]✓ {exec_name} removed from {install_dir}[/green]")
        return True

    except Exception as e:
        console.print(f"[red]Failed to remove {exec_name}: {e}[/red]")
        return False


def find_executable(exec_name: str, exec_path: str | None = None) -> str:
    """Find executable using simplified 3-mode logic.

    Args:
        exec_name: Name of the executable (e.g., 'claude', 'gemini', 'codex')
        exec_path: Optional explicit path provided by user

    Returns:
        Path to the executable

    Raises:
        InstallError: If executable cannot be found
    """
    # Mode 1: Direct executable path provided with --exec
    if exec_path:
        if Path(exec_path).exists() or shutil.which(exec_path):
            return exec_path
        else:
            raise InstallError(f"Provided exec path does not exist: {exec_path}")

    # Mode 2: Bundled executable if it exists in claif-owned directory
    from claif.install import get_install_location

    install_dir = get_install_location()
    bundled_path = install_dir / exec_name
    if bundled_path.exists():
        return str(bundled_path)

    # Mode 3: External executable via shutil.which
    external_path = shutil.which(exec_name)
    if external_path:
        return external_path

    # If nothing found, provide helpful error message
    package_map = {"claude": "@anthropic-ai/claude-code", "gemini": "@google/gemini-cli", "codex": "@openai/codex"}

    package_name = package_map.get(exec_name, exec_name)

    raise InstallError(
        f"{exec_name} executable not found. "
        f"Please run 'claif_{exec_name} install' to install and bundle {package_name}, "
        f"or install it globally with 'npm install -g {package_name}'"
    )


def install_provider(provider: str, package: str, exec_name: str) -> bool:
    """Install a provider completely (npm package + bundling + installation).

    Args:
        provider: Provider name (claude, gemini, codex)
        package: npm package name
        exec_name: Name of the executable to create

    Returns:
        True if installation succeeded, False otherwise.
    """
    console.print(f"[bold]Installing {provider} provider...[/bold]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        # Step 1: Install npm package
        task1 = progress.add_task(f"Installing {package}...", total=None)
        if not install_npm_package(package):
            return False
        progress.update(task1, completed=True)

        # Step 2: Bundle executable
        task2 = progress.add_task(f"Bundling {exec_name}...", total=None)
        if not bundle_executable(provider, exec_name):
            return False
        progress.update(task2, completed=True)

        # Step 3: Install bundled executable
        task3 = progress.add_task(f"Installing {exec_name}...", total=None)
        if not install_bundled_executable(provider, exec_name):
            return False
        progress.update(task3, completed=True)

    console.print(f"[green]🎉 {provider} provider installed successfully![/green]")
    console.print(f"[green]You can now use '{exec_name}' or 'claif_{provider}' commands[/green]")

    return True


def uninstall_provider(provider: str, exec_name: str) -> bool:
    """Uninstall a provider (remove bundled executable).

    Args:
        provider: Provider name (claude, gemini, codex)
        exec_name: Name of the executable to remove

    Returns:
        True if uninstallation succeeded, False otherwise.
    """
    console.print(f"[bold]Uninstalling {provider} provider...[/bold]")

    if uninstall_bundled_executable(exec_name):
        console.print(f"[green]✓ {provider} provider uninstalled successfully[/green]")
        return True
    else:
        console.print(f"[red]Failed to uninstall {provider} provider[/red]")
        return False


def bundle_claude() -> Optional[Path]:
    """Bundle Claude CLI with its yoga.wasm dependency."""
    try:
        # Get the claif-packages root directory (2 levels up from this file)
        claif_packages_root = Path(__file__).parent.parent.parent.parent.parent
        bundle_script = claif_packages_root / "bundle" / "bundle-optimized.sh"

        if not bundle_script.exists():
            logger.error(f"Bundle script not found: {bundle_script}")
            return None

        logger.info("Bundling Claude executable...")
        result = subprocess.run(
            ["bash", str(bundle_script)], cwd=bundle_script.parent, capture_output=True, text=True, check=True
        )

        # Check if bundled claude exists
        claude_dir = bundle_script.parent / "dist" / "claude"
        claude_exe = claude_dir / "claude"
        yoga_wasm = claude_dir / "yoga.wasm"

        if claude_exe.exists() and yoga_wasm.exists():
            logger.success("✓ Claude bundled successfully")
            return claude_dir
        else:
            logger.error("Claude bundling completed but files not found")
            return None

    except subprocess.CalledProcessError as e:
        logger.error(f"Claude bundling failed: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Error bundling Claude: {e}")
        return None


def create_wrapper_script(install_dir: Path, name: str, command: str) -> bool:
    """Create a wrapper script that calls the globally installed command."""
    wrapper_path = install_dir / name

    try:
        wrapper_content = f"""#!/usr/bin/env bash
# Wrapper script for {name}
# Generated by claif install

# Find the global bun installation
BUN="${{HOME}}/.bun/bin/bun"
if [[ ! -x "$BUN" ]]; then
    echo "Error: bun not found at $BUN" >&2
    exit 1
fi

# Execute the globally installed command
exec "$BUN" run --prefer-offline "{command}" "$@"
"""

        wrapper_path.write_text(wrapper_content)
        wrapper_path.chmod(0o755)

        logger.success(f"✓ Created wrapper script: {wrapper_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to create wrapper script for {name}: {e}")
        return False


def install_claude(install_dir: Path) -> bool:
    """Install Claude CLI with bundled approach."""
    try:
        # Bundle Claude
        claude_dir = bundle_claude()
        if not claude_dir:
            return False

        # Create installation directory for Claude
        claude_install_dir = install_dir / "claude"
        if claude_install_dir.exists():
            shutil.rmtree(claude_install_dir)

        # Copy the entire Claude directory (executable + yoga.wasm)
        shutil.copytree(claude_dir, claude_install_dir)

        # Create wrapper script that runs Claude from its directory
        wrapper_path = install_dir / "claude"
        wrapper_content = f"""#!/usr/bin/env bash
# Claude CLI wrapper script
# Generated by claif install

# Change to Claude directory and run the executable
cd "{claude_install_dir}" && exec ./claude "$@"
"""

        wrapper_path.write_text(wrapper_content)
        wrapper_path.chmod(0o755)

        logger.success(f"✓ Claude installed at {claude_install_dir}")
        return True

    except Exception as e:
        logger.error(f"Failed to install Claude: {e}")
        return False


def install_gemini(install_dir: Path) -> bool:
    """Install Gemini CLI using global npm + wrapper script."""
    if not install_npm_package_with_bun("@google/gemini-cli"):
        return False

    return create_wrapper_script(install_dir, "gemini", "@google/gemini-cli")


def install_codex(install_dir: Path) -> bool:
    """Install Codex CLI using global npm + wrapper script."""
    if not install_npm_package_with_bun("@openai/codex"):
        return False

    return create_wrapper_script(install_dir, "codex", "@openai/codex")


def install_providers(providers: List[str]) -> dict:
    """Install the specified providers using the bundled approach."""
    if not ensure_bun_installed():
        return {"success": False, "failed": providers, "message": "bun installation failed"}

    install_dir = get_install_location()
    results = {"installed": [], "failed": []}

    # Install npm packages globally first
    packages = {"claude": "@anthropic-ai/claude-code", "gemini": "@google/gemini-cli", "codex": "@openai/codex"}

    for provider in providers:
        if provider in packages:
            logger.info(f"Installing {packages[provider]}...")
            if not install_npm_package_with_bun(packages[provider]):
                results["failed"].append(provider)
                continue

    # Bundle all executables using the optimized script
    logger.info("Bundling executables...")
    bundle_dir = bundle_all_executables()
    if not bundle_dir:
        # If bundling failed, all providers failed
        results["failed"].extend([p for p in providers if p not in results["failed"]])
        return results

    # Install bundled executables
    for provider in providers:
        if provider in results["failed"]:
            continue

        logger.info(f"Installing {provider}...")
        if install_bundled_provider(provider, bundle_dir, install_dir):
            results["installed"].append(provider)
        else:
            results["failed"].append(provider)

    return results


def uninstall_providers(providers: List[str]) -> dict:
    """Uninstall the specified providers."""
    install_dir = get_install_location()
    bun_path = Path.home() / ".bun" / "bin" / "bun"

    results = {"uninstalled": [], "failed": []}

    for provider in providers:
        try:
            # Remove wrapper script
            wrapper_path = install_dir / provider
            if wrapper_path.exists():
                wrapper_path.unlink()
                logger.info(f"Removed wrapper script: {wrapper_path}")

            # Remove installation directory (for Claude)
            provider_dir = install_dir / provider
            if provider_dir.exists() and provider_dir.is_dir():
                shutil.rmtree(provider_dir)
                logger.info(f"Removed directory: {provider_dir}")

            # Uninstall global npm packages
            if provider == "claude":
                # Claude doesn't have a global npm package to uninstall
                pass
            elif provider == "gemini" and bun_path.exists():
                subprocess.run([str(bun_path), "remove", "-g", "@google/gemini-cli"], capture_output=True)
            elif provider == "codex" and bun_path.exists():
                subprocess.run([str(bun_path), "remove", "-g", "@openai/codex"], capture_output=True)

            results["uninstalled"].append(provider)
            logger.success(f"✓ {provider} uninstalled")

        except Exception as e:
            logger.error(f"Failed to uninstall {provider}: {e}")
            results["failed"].append(provider)

    return results
