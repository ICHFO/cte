from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

metadata = MetaData()
resources = Table("resources", metadata,
    Column("id", Integer, primary_key=True),
    Column("firstname", String(64)),
    Column("lastname", String(64)),
    Column("username", String(32))
)

skilss = Table("skills", metadata,
    Column("id", Integer, primary_key=True),
    Column("name"))