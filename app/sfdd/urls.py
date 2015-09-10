def includeme(config):
    from sfdd.renderer import json_renderer
    from sfdd.contexts import CompanyContext

    routes = {
        'companies': {
            'url': '/companies',
        },
        'company': {
            'url': '/companies/{company_id:\d+}',
            'context': CompanyContext
        },
    }

    for route_name, params in routes.items():
        context = params.get('context')
        config.add_route(route_name, params['url'], factory=context)

    config.add_renderer('json', json_renderer())
