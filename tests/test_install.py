"""Tests for claif.common.install module."""

import os
import platform
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from claif.common.install import (
    InstallError,
    get_install_dir,
    ensure_install_dir,
    check_bun_available,
    ensure_bun_installed,
    find_executable,
    install_provider,
    uninstall_provider
)
from claif.install import (
    get_install_location,
    install_all_tools,
    uninstall_all_tools
)


class TestInstallError:
    """Test InstallError exception."""
    
    def test_install_error(self):
        """Test InstallError creation."""
        error = InstallError("Installation failed")
        assert str(error) == "Installation failed"
        assert isinstance(error, Exception)


class TestInstallDirectory:
    """Test install directory functions."""
    
    @patch("platform.system")
    def test_get_install_dir_windows(self, mock_system):
        """Test getting install directory on Windows."""
        mock_system.return_value = "Windows"
        
        with patch.dict(os.environ, {"LOCALAPPDATA": "C:\\Users\\Test\\AppData\\Local"}):
            result = get_install_dir()
            assert result == Path("C:\\Users\\Test\\AppData\\Local\\Programs\\claif")
    
    @patch("platform.system")
    def test_get_install_dir_unix(self, mock_system):
        """Test getting install directory on Unix-like systems."""
        mock_system.return_value = "Linux"
        
        with patch("pathlib.Path.home", return_value=Path("/home/user")):
            result = get_install_dir()
            assert result == Path("/home/user/.local/bin")
    
    def test_ensure_install_dir(self, tmp_path):
        """Test ensuring install directory exists."""
        with patch("claif.common.install.get_install_dir", return_value=tmp_path / "install"):
            result = ensure_install_dir()
            
            assert result.exists()
            assert result.is_dir()
            assert result == tmp_path / "install"
    
    def test_ensure_install_dir_existing(self, tmp_path):
        """Test ensuring existing install directory."""
        install_dir = tmp_path / "existing"
        install_dir.mkdir()
        
        with patch("claif.common.install.get_install_dir", return_value=install_dir):
            result = ensure_install_dir()
            
            assert result == install_dir
            assert result.exists()


class TestBunInstallation:
    """Test bun installation functions."""
    
    @patch("shutil.which")
    def test_check_bun_available_found(self, mock_which):
        """Test checking when bun is available."""
        mock_which.return_value = "/usr/local/bin/bun"
        
        assert check_bun_available() is True
        mock_which.assert_called_once_with("bun")
    
    @patch("shutil.which")
    def test_check_bun_available_not_found(self, mock_which):
        """Test checking when bun is not available."""
        mock_which.return_value = None
        
        assert check_bun_available() is False
    
    @patch("pathlib.Path.home")
    def test_ensure_bun_installed_already_exists(self, mock_home):
        """Test ensure_bun_installed when bun already exists."""
        mock_home.return_value = Path("/home/user")
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.is_file", return_value=True):
                result = ensure_bun_installed()
                assert result is True
    
    @patch("subprocess.run")
    @patch("platform.system")
    @patch("pathlib.Path.home")
    def test_ensure_bun_installed_install(self, mock_home, mock_system, mock_run):
        """Test installing bun when not present."""
        mock_home.return_value = Path("/home/user")
        mock_system.return_value = "Linux"
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch("pathlib.Path.exists", return_value=False):
            result = ensure_bun_installed()
            
            assert result is True
            mock_run.assert_called_once()
            # Check that curl command was called
            args = mock_run.call_args[0][0]
            assert "curl" in args[0]
            assert "bun.sh" in str(args)
    
    # Commented out tests for undefined functions
    # TODO: Add these back when run_bun_install is implemented
    pass


class TestExecutableFinding:
    """Test executable finding functions."""
    
    @patch("shutil.which")
    def test_find_executable_in_path(self, mock_which):
        """Test finding executable in PATH."""
        mock_which.return_value = "/usr/bin/test-exe"
        
        result = find_executable("test-exe")
        
        assert result == Path("/usr/bin/test-exe")
        mock_which.assert_called_once_with("test-exe")
    
    @patch("shutil.which")
    @patch("pathlib.Path.home")
    def test_find_executable_in_home(self, mock_home, mock_which):
        """Test finding executable in home directory."""
        mock_which.return_value = None
        mock_home.return_value = Path("/home/user")
        
        locations = [
            Path("/home/user/.local/bin/test-exe"),
            Path("/home/user/.bun/bin/test-exe")
        ]
        
        def exists_side_effect(self):
            return self in locations
        
        with patch("pathlib.Path.exists", exists_side_effect):
            result = find_executable("test-exe")
            assert result in locations
    
    @patch("shutil.which")
    def test_find_executable_not_found(self, mock_which):
        """Test when executable is not found."""
        mock_which.return_value = None
        
        with patch("pathlib.Path.exists", return_value=False):
            result = find_executable("missing-exe")
            assert result is None


class TestProviderInstallation:
    """Test provider installation functions."""
    
    @patch("subprocess.run")
    def test_install_provider_pip(self, mock_run):
        """Test installing provider with pip."""
        mock_run.return_value = MagicMock(returncode=0)
        
        install_provider("test-provider", method="pip")
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "pip" in str(args)
        assert "install" in args
        assert "test-provider" in args
    
    @patch("subprocess.run")
    def test_install_provider_pipx(self, mock_run):
        """Test installing provider with pipx."""
        mock_run.return_value = MagicMock(returncode=0)
        
        install_provider("test-provider", method="pipx")
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "pipx" in args[0]
        assert "install" in args
        assert "test-provider" in args
    
    @patch("claif.common.install.ensure_bun_installed")
    @patch("claif.common.install.run_bun_install")
    def test_install_provider_bun(self, mock_bun_install, mock_ensure_bun):
        """Test installing provider with bun."""
        mock_ensure_bun.return_value = True
        
        install_provider("@test/provider", method="bun")
        
        mock_ensure_bun.assert_called_once()
        mock_bun_install.assert_called_once_with("@test/provider")
    
    def test_install_provider_invalid_method(self):
        """Test installing with invalid method."""
        with pytest.raises(InstallError) as exc_info:
            install_provider("test", method="invalid")
        
        assert "Unsupported install method" in str(exc_info.value)
    
    @patch("subprocess.run")
    def test_uninstall_provider_pip(self, mock_run):
        """Test uninstalling provider with pip."""
        mock_run.return_value = MagicMock(returncode=0)
        
        uninstall_provider("test-provider", method="pip")
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "pip" in str(args)
        assert "uninstall" in args
        assert "-y" in args
        assert "test-provider" in args


# Commented out TestBundledExecutables - functions not implemented yet
# class TestBundledExecutables:
#     """Test bundled executable functions."""
#     pass


class TestInstallIntegration:
    """Test installation integration scenarios."""
    
    @patch("subprocess.run")
    def test_install_flow_success(self, mock_run):
        """Test successful installation flow."""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Should not raise
        install_provider("test-package", method="pip")
        
        # Verify pip install was called
        assert mock_run.called
    
    @patch("subprocess.run")
    def test_install_flow_failure(self, mock_run):
        """Test failed installation flow."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Permission denied"
        )
        
        with pytest.raises(InstallError) as exc_info:
            install_provider("test-package", method="pip")
        
        assert "Failed to install" in str(exc_info.value)