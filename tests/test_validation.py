import json

from tests.support import AGENT, CASES, NAME, PLUGIN, SKILL, RepositoryTestCase


class MetadataTests(RepositoryTestCase):
    def test_valid_repository(self):
        self.assert_valid()

    def test_conventional_yaml_strings(self):
        for fields in (f"name: '{NAME}'\ndescription: >\n  A folded\n  description",
                       f'name: "{NAME}"\ndescription: "Quoted: description"'):
            with self.subTest(fields=fields):
                self.frontmatter(fields)
                self.sync_archive()
                self.assert_valid()

    def test_invalid_frontmatter_yaml(self):
        for description in ('"unterminated', "[unclosed", "!!python/object:builtins.object {}"):
            with self.subTest(description=description):
                self.frontmatter(f"name: {NAME}\ndescription: {description}")
                self.assert_invalid("YAML")

    def test_duplicate_frontmatter_key(self):
        self.frontmatter(f"name: wrong-name\nname: {NAME}\ndescription: Fixture")
        self.assert_invalid("duplicate")

    def test_frontmatter_requires_nonempty_strings(self):
        for value in ("null", "true", "123", "[a, b]", "{a: b}", '"  "', ""):
            with self.subTest(value=value):
                self.frontmatter(f"name: {NAME}\ndescription: {value}")
                self.assert_invalid("description")

    def test_frontmatter_exact_fields_and_name(self):
        for fields, error in (("description: Fixture", "name"),
                              (f"name: {NAME}", "description"),
                              ("name: wrong\ndescription: Fixture", "name"),
                              (f"name: {NAME}\ndescription: Fixture\nextra: value", "extra")):
            with self.subTest(fields=fields):
                self.frontmatter(fields)
                self.assert_invalid(error)

    def test_description_budget_uses_decoded_value(self):
        self.frontmatter(f'name: {NAME}\ndescription: "' + r"\u0078" * 1024 + '"')
        self.sync_archive()
        self.assert_valid()
        self.frontmatter(f"name: {NAME}\ndescription: " + "x" * 1024)
        self.sync_archive()
        self.assert_valid()
        self.frontmatter(f"name: {NAME}\ndescription: " + "x" * 1025)
        self.assert_invalid("1024")

    def test_host_metadata_must_be_safe_unique_yaml_mapping(self):
        for document in ("interface: [unclosed", "- not-a-mapping", "interface: {}\ninterface: {}",
                         "interface:\n  display_name: A\n  display_name: B", "!!python/object:builtins.object {}"):
            with self.subTest(document=document):
                self.write(AGENT, document)
                self.sync_archive()
                self.assert_invalid("openai.yaml")

    def test_host_fields_are_optional_but_typed_when_present(self):
        self.write(AGENT, "{}\n")
        self.sync_archive()
        self.assert_valid()
        for document in ("interface: []", "interface:\n  display_name: 3", 'interface:\n  default_prompt: "  "'):
            with self.subTest(document=document):
                self.write(AGENT, document)
                self.sync_archive()
                self.assert_invalid("interface")

    def test_missing_metadata_and_extra_source_files(self):
        original = (self.repo / AGENT).read_text(encoding="utf-8")
        (self.repo / AGENT).unlink()
        self.assert_invalid("openai.yaml")
        self.write(AGENT, original)
        self.write(f"skills/{NAME}/extra.txt", "unexpected")
        self.assert_invalid("Unexpected")

    def test_plugin_paths_must_reference_the_local_skill(self):
        for paths in ([], "not-a-list", [1], ["./skills/missing"], ["../outside"],
                      [str(self.repo / "skills" / NAME)], [f"./skills/{NAME}"] * 2):
            with self.subTest(paths=paths):
                plugin = self.read_json(PLUGIN)
                plugin["skills"] = paths
                self.write_json(PLUGIN, plugin)
                self.assert_invalid("skills")

    def test_plugin_json_errors_are_helpful(self):
        for document in ("{invalid", "[]", "null", '{"version": "a", "version": "b"}'):
            with self.subTest(document=document):
                self.write(PLUGIN, document)
                self.assert_invalid("plugin.json")


class ReleaseTests(RepositoryTestCase):
    def test_version_changes_are_not_pinned_to_a_release(self):
        major, minor, patch = map(int, self.version.split("."))
        self.set_version(f"{major}.{minor}.{patch + 1}")
        self.assert_valid()

    def test_invalid_semver_core(self):
        for version in ("00.1.2", "1.02.3", "1.2.03", "\u0661.2.3", "1.2", "v1.2.3"):
            with self.subTest(version=version):
                self.set_version(version)
                self.assert_invalid("VERSION")

    def test_plugin_version_must_match(self):
        plugin = self.read_json(PLUGIN)
        plugin["version"] = "mismatch"
        self.write_json(PLUGIN, plugin)
        self.assert_invalid("version")

    def test_readme_requires_one_visible_current_section(self):
        valid = (self.repo / "README.md").read_text(encoding="utf-8")
        for readme in (valid + "\n## What's New in v999.0.0\nOld summary\n",
                       valid.replace(f"v{self.version}", "v999.0.0") + "\n<!-- " + valid + " -->\n",
                       "```markdown\n" + valid + "```\n", "~~~markdown\n" + valid + "~~~\n"):
            with self.subTest(readme=readme):
                self.write("README.md", readme)
                self.assert_invalid("README")

    def test_readme_requires_a_visible_current_download_link(self):
        valid = (self.repo / "README.md").read_text(encoding="utf-8")
        link = valid[valid.index("[Download]"):]
        for readme in (valid.replace(link, "<!-- " + link + " -->"),
                       valid.replace(f"/download/v{self.version}/", "/download/v999.0.0/"),
                       valid.replace(link, "`" + link.strip() + "`\n"),
                       valid.replace(link, link.replace("[Download]", "![]"))):
            with self.subTest(readme=readme):
                self.write("README.md", readme)
                self.assert_invalid("README")

    def test_readme_ignores_nonvisible_historical_examples(self):
        valid = (self.repo / "README.md").read_text(encoding="utf-8")
        self.write("README.md", valid + "\n<!-- ## What's New in v0.0.0 -->\n"
                   "\n```markdown\n## What's New in v0.0.0\n```\n")
        self.assert_valid()

    def test_changelog_requires_current_real_date_and_body(self):
        for changelog in ("# Changelog\n", f"## {self.version} - 2026-02-30\n- Change\n",
                          f"## {self.version} - 2026-01-01\n\n",
                          f"<!-- ## {self.version} - 2026-01-01\n- Change\n -->\n",
                          f"## {self.version} - 2026-01-01\n- Change\n" * 2):
            with self.subTest(changelog=changelog):
                self.write("CHANGELOG.md", changelog)
                self.assert_invalid("CHANGELOG")
        (self.repo / "CHANGELOG.md").unlink()
        self.assert_invalid("CHANGELOG")


class EvalSchemaTests(RepositoryTestCase):
    def test_schema_version_is_an_integer_not_boolean_or_float(self):
        for value in (True, False, 1.0, "1", None, 2):
            with self.subTest(value=value):
                cases = self.read_json(CASES)
                cases["schema_version"] = value
                self.write_json(CASES, cases)
                self.assert_invalid("schema_version")

    def test_malformed_data_has_helpful_errors(self):
        for document in ("{invalid", "[]", "null", '{"schema_version":1,"schema_version":1}'):
            with self.subTest(document=document):
                self.write(CASES, document)
                self.assert_invalid("cases.json")

    def test_invalid_case_shapes_are_rejected_without_tracebacks(self):
        original = self.read_json(CASES)
        for value in (None, [], {"id": "fixture", "mode": []}):
            with self.subTest(value=value):
                cases = json.loads(json.dumps(original))
                cases["cases"][0] = value
                self.write_json(CASES, cases)
                self.assert_invalid("case")

    def test_case_field_invariants(self):
        original = self.read_json(CASES)
        for field, value in (("id", " "), ("id", "case-1"), ("mode", "unknown"), ("prompt", " "),
                             ("assertions", []), ("assertions", [3]), ("failure_conditions", [""])):
            with self.subTest(field=field, value=value):
                cases = json.loads(json.dumps(original))
                cases["cases"][0][field] = value
                self.write_json(CASES, cases)
                self.assert_invalid("case")
