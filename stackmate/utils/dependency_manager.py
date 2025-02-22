"""
Smart dependency management system for Stackmate.
"""

import json
import aiohttp
import asyncio
from typing import Dict, List, Tuple, Optional
import semver
from datetime import datetime, timedelta

class DependencyManager:
    def __init__(self):
        self.npm_registry = "https://registry.npmjs.org"
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)

    async def get_package_info(self, package_name: str) -> Optional[Dict]:
        """Fetch package information from npm registry with caching."""
        if package_name in self.cache:
            cache_entry = self.cache[package_name]
            if datetime.now() - cache_entry["timestamp"] < self.cache_ttl:
                return cache_entry["data"]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.npm_registry}/{package_name}") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.cache[package_name] = {
                            "data": data,
                            "timestamp": datetime.now()
                        }
                        return data
                    return None
        except Exception:
            return None

    def parse_version(self, version: str) -> Optional[semver.VersionInfo]:
        """Parse version string into semver.VersionInfo object."""
        try:
            return semver.VersionInfo.parse(version.replace("^", "").replace("~", ""))
        except ValueError:
            return None

    async def resolve_version(self, package_name: str, version_spec: str) -> str:
        """Resolve the best matching version for a package."""
        package_info = await self.get_package_info(package_name)
        if not package_info or "versions" not in package_info:
            return version_spec

        available_versions = list(package_info["versions"].keys())
        try:
            # Convert version spec to semver range
            if version_spec.startswith("^"):
                base_version = self.parse_version(version_spec)
                if base_version:
                    version_range = f">={base_version} <{base_version.major + 1}.0.0"
                else:
                    return version_spec
            elif version_spec.startswith("~"):
                base_version = self.parse_version(version_spec)
                if base_version:
                    version_range = f">={base_version} <{base_version.major}.{base_version.minor + 1}.0"
                else:
                    return version_spec
            else:
                version_range = version_spec

            # Find latest version matching the range
            matching_versions = []
            for v in available_versions:
                try:
                    if semver.match(v, version_range):
                        matching_versions.append(v)
                except ValueError:
                    continue

            if matching_versions:
                latest_version = max(matching_versions, key=lambda v: self.parse_version(v) or semver.VersionInfo(0))
                return f"^{latest_version}"
            
            return version_spec
        except Exception:
            return version_spec

    async def check_compatibility(self, dependencies: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
        """Check compatibility between dependencies and suggest updates."""
        updated_deps = {}
        warnings = []
        
        # First pass: Resolve all versions
        for pkg, version in dependencies.items():
            resolved_version = await self.resolve_version(pkg, version)
            updated_deps[pkg] = resolved_version
            
            if resolved_version != version:
                warnings.append(f"Updated {pkg} from {version} to {resolved_version} for better compatibility")

        # Second pass: Check peer dependencies
        for pkg, version in updated_deps.items():
            pkg_info = await self.get_package_info(pkg)
            if not pkg_info:
                continue

            version_without_caret = version.replace("^", "")
            if version_without_caret not in pkg_info["versions"]:
                # Try to find the closest version
                available_versions = list(pkg_info["versions"].keys())
                matching_versions = []
                for v in available_versions:
                    try:
                        if semver.match(v, f">={version_without_caret}"):
                            matching_versions.append(v)
                    except ValueError:
                        continue

                if matching_versions:
                    version_without_caret = min(
                        matching_versions,
                        key=lambda v: abs((self.parse_version(v) or semver.VersionInfo(0)).major - (self.parse_version(version_without_caret) or semver.VersionInfo(0)).major)
                    )
                    updated_deps[pkg] = f"^{version_without_caret}"
                    warnings.append(f"Updated {pkg} to closest available version: {version_without_caret}")
                continue

            latest_version = pkg_info["versions"][version_without_caret]
            peer_deps = latest_version.get("peerDependencies", {})
            
            for peer, required_version in peer_deps.items():
                if peer in updated_deps:
                    current_version = updated_deps[peer].replace("^", "")
                    try:
                        if not semver.match(current_version, required_version):
                            # Try to find a version that satisfies both
                            peer_info = await self.get_package_info(peer)
                            if peer_info:
                                available_versions = list(peer_info["versions"].keys())
                                matching_versions = []
                                for v in available_versions:
                                    try:
                                        if semver.match(v, required_version):
                                            matching_versions.append(v)
                                    except ValueError:
                                        continue

                                if matching_versions:
                                    best_version = max(
                                        matching_versions,
                                        key=lambda v: self.parse_version(v) or semver.VersionInfo(0)
                                    )
                                    updated_deps[peer] = f"^{best_version}"
                                    warnings.append(
                                        f"Updated {peer} to {best_version} to satisfy peer dependency "
                                        f"requirement from {pkg} ({required_version})"
                                    )
                    except Exception:
                        warnings.append(f"Could not verify compatibility between {pkg} and {peer}")

        return updated_deps, warnings

    async def analyze_dependencies(self, dependencies: Dict[str, str]) -> Dict:
        """Analyze dependencies for security, updates, and compatibility."""
        updated_deps, warnings = await self.check_compatibility(dependencies)
        
        # Group warnings by type
        analysis = {
            "updated_dependencies": updated_deps,
            "compatibility_warnings": [w for w in warnings if "compatibility" in w.lower()],
            "version_updates": [w for w in warnings if "updated" in w.lower()],
            "security_warnings": [],  # Would integrate with security advisory APIs
            "recommendations": []
        }
        
        # Add general recommendations
        if len(updated_deps) > 10:
            analysis["recommendations"].append(
                "Consider using a monorepo setup with tools like Turborepo for better dependency management"
            )
        
        typescript_deps = any(pkg.startswith("@types/") for pkg in dependencies)
        if not typescript_deps and "typescript" in dependencies:
            analysis["recommendations"].append(
                "Add corresponding DefinitelyTyped packages (@types/*) for better TypeScript support"
            )
        
        return analysis 