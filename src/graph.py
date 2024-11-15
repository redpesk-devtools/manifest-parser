"""Implementation of the graph subcommand"""

from io import TextIOWrapper
import logging
import os
import shutil
import subprocess

from common import load_manifest

IDT = "    "  # indentation
MANIFEST_PATH_KEY = "__manifest_file_path"  # key added in "graph" method
MAN_ID = "id"
MAN_TARGETS = "targets"
MAN_BINDINGS = "provided-binding"
TGT_ID = "target"
TGT_CONTENT = "content"
TGT_CONTENT_TYPE = "type"
TGT_CONTENT_SRC = "src"
TGT_PROVIDED_APIS = "provided-api"
TGT_REQUIRED_APIS = "required-api"
TGT_REQUIRED_BINDINGS = "required-binding"
BDG_NAME = "name"
BDG_VALUE = "value"
API_NAME = "name"


def _manifest_id_to_package_id(manifest_id: str) -> str:
    """Transforms a manifest ID to a PlantUML package ID.
    Arg: manifest ID, i.e. "my-application"
    Returns: PlantUML package ID, i.e. "my_application_manifest"
    """
    res = manifest_id.replace("-", "_")
    res += "_manifest"
    return res


def _api_name_to_interface_id(api_name: str) -> str:
    """Transforms an API name to a PlantUML interface ID.
    Arg: API name, i.e. "my-api"
    Returns: PlantUML interface ID, i.e. "my_api_api"
    """
    res = api_name.replace("-", "_")
    res += "_api"
    return res


def _binding_name_to_artifact_id(binding_name: str) -> str:
    """Transforms a binding name to a PlantUML artifact ID.
    Arg: binding name, i.e. "my-binding"
    Returns: PlantUML artifact ID, i.e. "my_binding_binding"
    """
    res = binding_name.replace("-", "_").replace("/", "_").replace(".", "_")
    res += "_binding"
    return res


def _generate_binding_artifact(binding: dict, out: TextIOWrapper) -> str:
    artid = _binding_name_to_artifact_id(binding[BDG_NAME])
    out.write(f"artifact {artid} [\n")  # start binding
    out.write(f"{IDT}name = **{binding[BDG_NAME]}**\n")
    out.write(f'{IDT}value = ""{binding[BDG_VALUE]}""\n')
    out.write("]\n")  # end binding
    return artid


def _generate_puml_manifest_resources(man: dict, out: TextIOWrapper):
    packid = _manifest_id_to_package_id(man[MAN_ID])
    out.write(f"'{man[MANIFEST_PATH_KEY]}\n")
    # manifest and targets
    out.write(f"package {man[MAN_ID]} as {packid} {{\n")  # start manifest
    for tgt in man.get(MAN_TARGETS, []):
        out.write(f"{IDT}component {packid}.{tgt[TGT_ID]} [\n")  # start target
        out.write(f"{2*IDT}**Target: {tgt[TGT_ID]}**\n")
        out.write(f"{2*IDT}type = {tgt[TGT_CONTENT][TGT_CONTENT_TYPE]}\n")
        out.write(f'{2*IDT}src = ""{tgt[TGT_CONTENT][TGT_CONTENT_SRC]}""\n')
        out.write(f"{IDT}]\n")  # end target
    out.write("}\n")  # end manifest
    # manifest provided bindings
    for binding in man.get(MAN_BINDINGS, []):
        artid = _generate_binding_artifact(binding, out)
        out.write(f"{packid} ..> {artid}: provides\n")  # link binding to manifest
    # target provided APIs & local-only required bindings
    for tgt in man.get(MAN_TARGETS, []):
        for api in tgt.get(TGT_PROVIDED_APIS, []):
            itfid = _api_name_to_interface_id(api[API_NAME])
            out.write(f"() {api[API_NAME]} as {itfid}\n")  # api
            out.write(
                f"{packid}.{tgt[TGT_ID]} ..> {itfid}: provides\n"
            )  # link api to manifest
        for binding in tgt.get(TGT_REQUIRED_BINDINGS, []):
            if binding[BDG_VALUE] == "local":
                _generate_binding_artifact(binding, out)


def _generate_puml_manifest_requires(man: dict, out: TextIOWrapper):
    packid = _manifest_id_to_package_id(man[MAN_ID])
    out.write(f"'{man[MANIFEST_PATH_KEY]}\n")
    for tgt in man.get(MAN_TARGETS, []):
        for binding in tgt.get(TGT_REQUIRED_BINDINGS, []):
            artid = _binding_name_to_artifact_id(binding[BDG_NAME])
            out.write(f"{packid}.{tgt[TGT_ID]} --> {artid}: requires\n")
        for api in tgt.get(TGT_REQUIRED_APIS, []):
            itfid = _api_name_to_interface_id(api[API_NAME])
            out.write(f"{packid}.{tgt[TGT_ID]} --> {itfid}: requires\n")


def _generate_puml(manifests: list[dict], out: TextIOWrapper, diagram_name: str):
    out.write(f"@startuml {diagram_name}\n\n")
    # "requires" must be generated in a second pass, otherwise there may
    # be arrows pointing to undeclared resources, hence implicitly
    # declaring them, and preventing the real declaration later on

    # first pass: package, targets, bindings, APIs and provides arrows
    out.write("' ##### DECLARED RESOURCES #####\n\n")
    for manifest in manifests:
        _generate_puml_manifest_resources(manifest, out)
        out.write("\n")
    # second pass: requires arrows
    out.write("' ##### REQUIRED RESOURCES #####\n\n")
    for manifest in manifests:
        _generate_puml_manifest_requires(manifest, out)
        out.write("\n")
    out.write("@enduml\n")


def graph(
    output: str,
    paths: list[str],
    keep_puml: bool,
    overwrite: bool,
    no_check: bool,
    logger: logging.Logger,
) -> bool:
    """Generates a PlantUML graph from multiple manifest files.
    The graph shows bindings and APIs provided and required by the manifests and
    targets. If the "plantuml" executable cannot be found, the .puml diagram
    description file will be kept. Otherwise, an .svg file is produced and the
    .puml file deleted.
    Args:
        output: file name for the outputs (<output>.puml or <output>.svg)
        paths: list of manifest file paths
        logger: logger object
    Returns: False on error, True if everything went OK
    """
    logger = logger.getChild(__name__)

    # load manifests
    manifests = []
    for path in paths:
        manifest = load_manifest(path, logger)
        if manifest is None:
            return False
        manifest[MANIFEST_PATH_KEY] = path
        manifests.append(manifest)
    logger.info("%i manifests loaded", len(manifests))

    # check they are valid
    pass

    # generate diagram description
    out_puml_path = f"{output}.puml"
    if not overwrite:
        if os.path.exists(out_puml_path):
            logger.error(
                "A dir or file already exists at %s (use --overwrite)",
                out_puml_path,
            )
            return False
    with open(out_puml_path, mode="w", encoding="utf-8") as out_puml:
        _generate_puml(manifests, out_puml, output)

    # render to svg
    out_svg_path = f"{output}.svg"
    if not overwrite:
        if os.path.exists(out_svg_path):
            logger.error(
                "A dir or file already exists at %s (use --overwrite)", out_svg_path
            )
            if not keep_puml:
                os.remove(out_puml_path)
            return False
    plantuml = shutil.which("plantuml")
    if plantuml is None:
        logger.error(
            "plantuml executable not found in PATH, unable to render the diagram"
        )
        if not keep_puml:
            os.remove(out_puml_path)
        return False
    try:
        subprocess.run(["plantuml", "-tsvg", out_puml_path], check=True)
    except subprocess.CalledProcessError:
        logger.error(
            "plantuml failed to render the diagram correctly,"
            " check output image for details"
        )
        return False

    if not keep_puml:
        os.remove(out_puml_path)
    return True
