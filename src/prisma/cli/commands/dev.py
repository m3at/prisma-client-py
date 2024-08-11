from typing import Any, Optional, cast

import click

from .. import options
from ..utils import error, generate_client
from ...utils import module_exists, maybe_async_run, temp_env_update


@click.group()
def _cli() -> None:
    """Commands for developing Prisma Client Python"""


# There are some weird false positives that `cli` being a `Group` introduces
# for some reason. Fixing the errors for one type checker causes errors in an another
# so just switch to Any for the time being as this is internal and only used once, directly
# below this line.
cli: Any = cast(Any, _cli)


@cli.command()  # type: ignore[misc]
@options.schema
@options.skip_generate
def playground(schema: Optional[str], skip_generate: bool) -> None:
    """Run the GraphQL playground"""
    if skip_generate and not module_exists('prisma.client'):
        error('Prisma Client Python has not been generated yet.')
    else:
        generate_client(schema=schema, reload=True)

    from ... import Prisma
    from ...engine import QueryEngine, BaseQueryEngine

    client = Prisma()
    engine_class = client._engine_class
    if issubclass(engine_class, BaseQueryEngine):
        with temp_env_update({'__PRISMA_PY_PLAYGROUND': '1'}):
            maybe_async_run(client.connect)

        # TODO: this is the result of a badly designed class
        engine = cast(QueryEngine, client._engine)
        assert engine.process is not None, 'Engine process unavailable for some reason'
        engine.process.wait()
    else:  # pragma: no cover
        error(f'Unsupported engine type: "{engine_class}"')
