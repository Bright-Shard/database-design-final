{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  name = "db-design-shell";
  packages = with pkgs; [
    podman
    python313

    # LSPs
    basedpyright
    ruff

    # Pip dependencies
    (python313.withPackages (
      pypkgs: with pypkgs; [
        flask
        psycopg
        pydantic
      ]
    ))
  ];
}
