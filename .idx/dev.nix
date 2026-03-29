{ pkgs, ... }: {
  # https://devenv.sh/basics/
  #
  # Complete the following steps to get started:
  #
  # 1. Check a field's options with `nix-do nix-doc <field>`.
  # 2. Add a library to the environment with `nix-do nix-search <library>`.
  # 3. Start a new shell with `nix-do`.
  #
  # For more information, see https://devenv.sh/guides/adding-languages/.

  # https://devenv.sh/reference/options/
  languages.nix.enable = true;

  # Set the shell's prompt.
  # https://devenv.sh/reference/options/#env
  env.PRISMA_DML_PATH = "prisma/schema.prisma";
  env.DEVENVCG = "true";

  # Add packages to the environment.
  # https://devenv.sh/reference/options/#packages
  packages = [
    pkgs.nodejs_20
    pkgs.nodePackages.npm
    (pkgs.python3.withPackages
      (ps:
        with ps; [
          # Add your python packages here
        ]))
  ];

  # Set environment variables.
  # https://devenv.sh/reference/options/#env
  env.PORT = "8000";

  # Start services when the environment is activated.
  # https://devenv.sh/reference/options/#services
  # services.nginx.enable = true;
  # services.nginx.virtualHosts."hello.com".root = ./public;

  # Set up a pre-commit hook that formats all files.
  # https://devenv.sh/reference/options/#pre-commithooks
  pre-commit.hooks.alejandra.enable = true;
}