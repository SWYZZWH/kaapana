#!/usr/bin/env python3
import os
import sys
import time

# Ensure local imports work
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KAAPANA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from build_helper.build_utils import BuildUtils  # type: ignore
from build_helper.container_helper import Container  # type: ignore


def main():
    # Config
    default_registry = os.environ.get(
        "DEFAULT_REGISTRY", "docker.io/zwh188222/densematrix"
    )
    image_filter = os.environ.get("IMAGE_FILTER", "").strip()

    # Init BuildUtils
    # Init logging minimally (BuildUtils.init would set more, but we just need logger)
    BuildUtils.init()
    if getattr(BuildUtils, "logger", None) is None:
        import logging

        logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
        BuildUtils.logger = logging.getLogger("runner")
    BuildUtils.kaapana_dir = KAAPANA_DIR
    BuildUtils.build_dir = os.path.join(KAAPANA_DIR, "build")
    os.makedirs(BuildUtils.build_dir, exist_ok=True)

    BuildUtils.default_registry = default_registry
    BuildUtils.enable_build_kit = 1
    BuildUtils.exit_on_error = False
    BuildUtils.skip_push_no_changes = True
    BuildUtils.push_to_microk8s = False
    BuildUtils.http_proxy = None
    # Avoid overly broad ignore patterns ("ci" matches many paths like "policy").
    BuildUtils.build_ignore_patterns = [
        "templates_and_examples",
        # Safe ignores only
    ]

    # Optional whitelist of image names to build (comma-separated)
    core_list_env = os.environ.get("CORE_IMAGES", "").strip()
    core_images = [x.strip() for x in core_list_env.split(",") if x.strip()]

    # Stub repo info resolver to avoid git dependency in submodule context
    def _stub_repo_info(_repo_dir: str):
        # version, branch, last_commit, timestamp
        from datetime import datetime

        return (
            os.environ.get("KAAPANA_BUILD_VERSION", "0.5.1"),
            os.environ.get("KAAPANA_BUILD_BRANCH", "manual"),
            os.environ.get("KAAPANA_LAST_COMMIT", "0000000"),
            datetime.now().astimezone().replace(microsecond=0).isoformat(),
        )

    BuildUtils.get_repo_info = _stub_repo_info  # type: ignore[attr-defined]

    # Init container engine
    Container.init_containers(container_engine="docker", enable_build=True, enable_push=True)

    # Collect all container Dockerfiles
    containers = Container.collect_containers()

    # Optional filter by substring
    if image_filter:
        containers = [c for c in containers if image_filter in (c.image_name or "")]

    # Optional whitelist selection plus required local-only base images
    if core_images:
        selected = [c for c in containers if (c.image_name or "") in core_images]
        # Include required local-only base images transitively
        required_base_names = set()
        frontier = list(selected)
        visited = set()
        while frontier:
            c = frontier.pop()
            if id(c) in visited:
                continue
            visited.add(id(c))
            for b in getattr(c, "base_images", []) or []:
                if "local-only/" in b.tag:
                    base_name = b.tag.split("/")[1].split(":")[0]
                    if base_name not in required_base_names:
                        required_base_names.add(base_name)
                        # Find the container object that builds this base image
                        for cc in containers:
                            if (cc.image_name or "") == base_name:
                                frontier.append(cc)
        base_containers = [c for c in containers if (c.image_name or "") in required_base_names]
        selected.extend(base_containers)
        # De-duplicate
        seen = set()
        filtered = []
        for c in selected:
            key = c.image_name or c.path
            if key not in seen:
                seen.add(key)
                filtered.append(c)
        containers = filtered

    # Ensure local-only base images are built first
    containers = sorted(containers, key=lambda c: 0 if getattr(c, "registry", None) == "local-only" else 1)

    total = len(containers)
    print(f"[runner] Total containers to build/push: {total}")
    built = 0
    pushed = 0
    start = time.time()

    for idx, container in enumerate(containers, start=1):
        # Derive flat repository tag: namespace/repo:component-version
        comp = container.image_name or "image"
        ver = container.repo_version or os.environ.get("KAAPANA_BUILD_VERSION", "0.5.1")
        flat_tag = f"{default_registry}:{comp}-{ver}"
        container.build_tag = flat_tag
        # Keep original to decide on post-tagging and push rules
        original_registry = getattr(container, "registry", None)
        try:
            container.check_prebuild()
            issue, duration = container.build()
            if container.container_build_status in ("built", "nothing_changed"):
                built += 1
                # If this was a local-only base image, ensure local tag exists for downstream builds
                if original_registry == "local-only":
                    os.system(f"docker tag {flat_tag} {container.tag}")
            else:
                # Log build failure details if present
                if issue and isinstance(issue, dict) and issue.get("output") is not None:
                    out = issue.get("output")
                    try:
                        so = (out.stdout or "").splitlines()[-60:]
                        se = (out.stderr or "").splitlines()[-60:]
                        print(f"[runner] BUILD STDOUT tail for {container.tag}:\n" + "\n".join(so))
                        print(f"[runner] BUILD STDERR tail for {container.tag}:\n" + "\n".join(se))
                    except Exception:
                        pass
            # Push
            if original_registry == "local-only":
                # Skip pushing local-only base images
                pass
            else:
                # Allow push even if Container thinks it's local image
                container.local_image = False
                p_issue, p_duration = container.push()
                if container.container_push_status != "pushed" and p_issue:
                    out = p_issue.get("output")
                    if out is not None:
                        try:
                            so = (out.stdout or "").splitlines()[-60:]
                            se = (out.stderr or "").splitlines()[-60:]
                            print(f"[runner] PUSH STDOUT tail for {container.tag}:\n" + "\n".join(so))
                            print(f"[runner] PUSH STDERR tail for {container.tag}:\n" + "\n".join(se))
                        except Exception:
                            pass
            if container.container_push_status == "pushed":
                pushed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[runner] ERROR for {container.tag}: {exc}")

        if idx % 5 == 0 or idx == total:
            elapsed = int(time.time() - start)
            print(
                f"[runner] Progress {idx}/{total} | built={built} pushed={pushed} | elapsed={elapsed}s"
            )

    elapsed = int(time.time() - start)
    print(
        f"[runner] DONE | total={total} built={built} pushed={pushed} | elapsed={elapsed}s | registry={default_registry}"
    )


if __name__ == "__main__":
    main()


