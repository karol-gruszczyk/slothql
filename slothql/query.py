from graphql import Source, parse, validate, GraphQLSchema
from graphql.error import format_error, GraphQLSyntaxError
from graphql.execution import execute, ExecutionResult


class QueryExecutor:
    def __init__(self, schema: GraphQLSchema) -> None:
        self.schema = schema
        assert isinstance(schema, GraphQLSchema), f'schema has to be of type GraphQLSchema, not {self.schema}'

    def query(self, query: str) -> dict:
        assert isinstance(query, str), f'Expected query string, got {query}'

        result = self.execute_query(query)
        if result.invalid:
            return {'errors': [self.format_error(error) for error in result.errors]}
        return {'data': result.data}

    def execute_query(self, query: str) -> ExecutionResult:
        source = Source(query)

        try:
            document_ast = parse(source=source)
        except GraphQLSyntaxError as e:
            return ExecutionResult(errors=[e], invalid=True)

        validation_errors = validate(self.schema, document_ast)
        if validation_errors:
            return ExecutionResult(errors=validation_errors, invalid=True)
        return execute(self.schema, document_ast)

    @classmethod
    def format_error(cls, error: Exception) -> dict:
        if isinstance(error, GraphQLSyntaxError):
            return format_error(error)
        return {'message': str(error)}
