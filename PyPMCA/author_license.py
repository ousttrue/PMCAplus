import dataclasses


@dataclasses.dataclass
class AuthorLicense:
    authors: list[str] = dataclasses.field(default_factory=list)
    licenses: list[str] = dataclasses.field(default_factory=list)
    script_fin: list[str] = dataclasses.field(default_factory=list)

    @staticmethod
    def create(name: str) -> "AuthorLicense":
        author_license = AuthorLicense()
        if name != "":
            author_license.authors = ["Unknown"]
            author_license.licenses = ["Nonfree"]
        return author_license

    def get_authors(self) -> str:
        return " ".join(self.authors)

    def get_licenses(self) -> str:
        return " ".join(self.licenses)

    def append_author(self, author: str):
        if author not in self.authors:
            self.authors.append(author)

    def append_license(self, license: str):
        if license not in self.licenses:
            self.licenses.append(license)

    def execute_scripts(self):
        for x in self.script_fin:
            argv = x.split()
            fp = open(argv[0], "r", encoding="utf-8-sig")
            script = fp.read()
            exec(script)
            fp.close
