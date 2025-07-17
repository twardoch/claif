# this_file: Formula/claif.rb
# Homebrew formula for Claif

class Claif < Formula
  desc "Unified command-line interface framework for AI language models"
  homepage "https://github.com/twardoch/claif"
  url "https://github.com/twardoch/claif/archive/refs/tags/v1.0.31.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000"
  license "MIT"

  depends_on "python@3.12"
  depends_on "node" => :optional  # For provider CLI installations

  def install
    # Install Python package
    virtualenv_install_with_resources
    
    # Create wrapper script
    (bin/"claif").write <<~EOS
      #!/bin/bash
      "#{libexec}/bin/python" -m claif.cli "$@"
    EOS
    
    # Install provider CLIs if node is available
    if build.with?("node")
      system "#{libexec}/bin/claif", "install", "all"
    end
  end

  def caveats
    <<~EOS
      Claif has been installed! Get started with:
        claif --help
        claif query "Hello, world!"
        
      To install AI provider CLIs:
        claif install
        
      Provider packages can be installed separately:
        pip install claif_cla  # Claude
        pip install claif_gem  # Gemini
        pip install claif_cod  # Codex
    EOS
  end

  test do
    system "#{bin}/claif", "--version"
    system "#{bin}/claif", "--help"
  end
end