from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import DC, RDF
from logs import app_logger
from utils.db import connect_DB
from utils.prefixes import bind_prefix


class WorkflowGraph(object):
    """Create WorkflowGraph class."""

    @classmethod
    def workflow(cls, db_conf=None, namespace_conf=None):
        """Build workflow graph with associated information."""
        workflow_graph = Graph()

        # bind prefixes
        bind_prefix(workflow_graph)
        KAISA = Namespace('http://helsinki.fi/library/onto#')

        db_cursor = connect_DB()

        cls.fetch_workflows(db_cursor, workflow_graph, KAISA)
        cls.fetch_steps(db_cursor, workflow_graph, KAISA)
        cls.fetch_steps_sequence(db_cursor, workflow_graph, KAISA)
        db_cursor.connection.close()
        return workflow_graph

    @staticmethod
    def fetch_workflows(db_cursor, graph, namespace):
        """Create Workflow ID and description."""
        # Get general workflow information on the last executed workflow
        db_cursor.execute("""
             SELECT ppl_model.id AS 'workflowId',
             ppl_model.description AS 'description',
             ppl_model.name AS 'workflowTitle'
             FROM ppl_model
             ORDER BY ppl_model.id DESC LIMIT 1
        """)

        result_set = db_cursor.fetchall()

        for row in result_set:
            graph.add((URIRef("{0}workflow{1}".format(namespace,
                                                      row['workflowId'])),
                       RDF.type,
                      namespace.Workflow))
            graph.add((URIRef("{0}workflow{1}".format(namespace,
                                                      row['workflowId'])),
                      DC.title,
                      Literal(row['workflowTitle'])))
            graph.add((URIRef("{0}workflow{1}".format(namespace,
                                                      row['workflowId'])),
                      DC.description,
                      Literal(row['description'])))
            app_logger.info('Construct metadata for Workflow{0}.'
                            .format(row['workflowId']))
        return graph

    @staticmethod
    def fetch_steps(db_cursor, graph, namespace):
        """Create Steps ID and description."""
        # Get steps information
        db_cursor.execute("""
        SELECT dpu_instance.id AS 'stepId', dpu_instance.name AS 'stepTitle',
        dpu_instance.description AS 'description',
        dpu_template.name AS 'templateName', ppl_model.id AS 'workflowId'
        FROM ppl_model, dpu_template, dpu_instance INNER JOIN
        ppl_node ON ppl_node.instance_id=dpu_instance.id
             WHERE ppl_node.graph_id = (
                SELECT id
                FROM ppl_model
                ORDER BY ppl_model.id DESC LIMIT 1)
            AND dpu_instance.dpu_id = dpu_template.id
        """)

        result_set = db_cursor.fetchall()

        PWO = Namespace('http://purl.org/spar/pwo/')

        for row in result_set:
            graph.add((URIRef("{0}step{1}".format(namespace, row['stepId'])),
                      RDF.type,
                      namespace.Step))
            graph.add((URIRef("{0}step{1}".format(namespace, row['stepId'])),
                      DC.title,
                      Literal(row['stepTitle'])))
            graph.add((URIRef("{0}step{1}".format(namespace, row['stepId'])),
                      DC.description,
                      Literal(row['description'])))
            graph.add((URIRef("{0}workflow{1}".format(namespace,
                                                      row['workflowId'])),
                      PWO.hasStep,
                      URIRef("{0}step{1}".format(namespace, row['stepId']))))
            app_logger.info('Construct step metadata for Step{0}.'
                            .format(row['stepId']))
        return graph

    @staticmethod
    def fetch_steps_sequence(db_cursor, graph, namespace):
        """Create Steps sequence."""
        # Get steps linkage
        db_cursor.execute("""
        SELECT
          FromStep.instance_id AS 'fromStep',
          ToStep.instance_id AS 'toStep'
        FROM ppl_edge
        INNER JOIN ppl_node AS FromStep
          ON FromStep.id=ppl_edge.node_from_id
        INNER JOIN ppl_node AS ToStep
          ON ToStep.id=ppl_edge.node_to_id
        """)

        result_set = db_cursor.fetchall()

        PWO = Namespace('http://purl.org/spar/pwo/')

        for row in result_set:
            graph.add((URIRef("{0}step{1}".format(namespace, row['fromStep'])),
                      PWO.hasNextStep,
                      URIRef("{0}step{1}".format(namespace, row['toStep']))))
            app_logger.info('Fetch steps sequence between steps Step{0} '
                            'and Step{1}.'.format(row['fromStep'],
                                                  row['toStep']))
        return graph


def workflow_get_output(serialization=None):
    """Construct the Ouput for the Get request."""
    data = WorkflowGraph()
    workflow_graph = data.workflow()
    if len(workflow_graph) > 0 and serialization is None:
        result = workflow_graph.serialize(format='turtle')
    elif len(workflow_graph) > 0 and serialization is not None:
        result = workflow_graph.serialize(format=serialization)
    elif len(workflow_graph) == 0:
        result = "No Workflow to be loaded."
    app_logger.info('Constructed Output for UnifiedViews Workflow '
                    'metadata enrichment finalized and set to API.')
    return result
