from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class Profile:
    provider: str
    model: str
    description: str
    base_url: str | None = None

@dataclass
class FeaturesConfig:
    blog_generation: bool = False
    tweet_generation: bool = False
    tweet_generation_locked: bool = False

@dataclass
class AgastyaConfig:
    default_profile: str = "local"
    profiles: dict[str, Profile] = field(default_factory=dict)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)

class ConfigLoader:
    def __init__(self, config_dir: Path | None = None):
        if config_dir is None:
            config_dir = Path.home() / ".agastya"
        self.config_dir = config_dir

    def get_default_config_dir(self) -> Path:
        return self.config_dir

    def get_manas_registry_path(self) -> Path:
        return self.config_dir / "manas.yaml"

    def load(self) -> AgastyaConfig:
        config_path = self.config_dir / "config.yaml"
        if not config_path.exists():
            return self._get_default_config()

        raw_data = self._parse_yaml(config_path)
        return self._merge_defaults(raw_data)

    def _parse_yaml(self, path: Path) -> dict:
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except yaml.YAMLError as exc:
            raise ValueError(f"Failed to parse config.yaml: {exc}")

    def _get_default_config(self) -> AgastyaConfig:
        return AgastyaConfig(
            default_profile="local",
            profiles={
                "local": Profile(
                    provider="ollama",
                    model="llama3",
                    description="Offline, private"
                )
            },
            features=FeaturesConfig()
        )

    def _merge_defaults(self, raw: dict) -> AgastyaConfig:
        default_config = self._get_default_config()

        # default_profile
        default_profile = raw.get("default_profile", default_config.default_profile)

        # features
        features_data = raw.get("features", {})
        features = FeaturesConfig(
            blog_generation=features_data.get("blog_generation", default_config.features.blog_generation),
            tweet_generation=features_data.get("tweet_generation", default_config.features.tweet_generation),
            tweet_generation_locked=features_data.get("tweet_generation_locked", default_config.features.tweet_generation_locked)
        )

        # profiles
        profiles = {}
        profiles_data = raw.get("profiles", {})
        for name, profile_data in profiles_data.items():
            profiles[name] = Profile(
                provider=profile_data.get("provider", "openai"),
                model=profile_data.get("model", "gpt-4"),
                description=profile_data.get("description", ""),
                base_url=profile_data.get("base_url")
            )
        
        # If the default profile is missing but we have our fallback ones, ensure we have the default one
        if not profiles:
            profiles = default_config.profiles
        
        # If 'local' is the default_profile but has no entry since profiles exist and override
        if default_profile not in profiles and "local" in default_config.profiles and default_profile == "local":
             profiles["local"] = default_config.profiles["local"]

        return AgastyaConfig(
            default_profile=default_profile,
            profiles=profiles,
            features=features
        )
