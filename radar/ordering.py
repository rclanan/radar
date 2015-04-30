from flask import request, abort, url_for
from sqlalchemy import desc


ASCENDING = 'asc'
DESCENDING = 'desc'


def order_by_from_request(default, options):
    order_by = request.args.get('order_by')

    if order_by is None:
        return default
    elif order_by in options:
        return order_by
    else:
        abort(404)


def order_direction_from_request(default):
    order_direction = request.args.get('order_direction')

    if order_direction is None:
        return default
    elif order_direction == ASCENDING:
        return ASCENDING
    elif order_direction == DESCENDING:
        return DESCENDING
    else:
        abort(404)


def order_query(query, order_by_map, default_order_by=None, default_order_direction=ASCENDING):
    order_by = order_by_from_request(default_order_by, order_by_map.keys())
    order_direction = order_direction_from_request(default=default_order_direction)

    clause = order_by_map[order_by]

    if order_direction == DESCENDING:
        clause = desc(clause)

    ordering = Ordering(order_by, order_direction)

    return query.order_by(clause), ordering


class Ordering(object):
    def __init__(self, column, direction):
        self.column = column
        self.direction = direction

    def reverse(self, column):
        if self.column == column:
            if self.direction == ASCENDING:
                return DESCENDING
            else:
                return ASCENDING

    def is_ordered_by(self, column):
        return self.column == column


def url_for_order_by(order_by, order_direction):
    args = request.args.copy()
    args.update(request.view_args)

    # Back to the first page
    args.pop('page', None)

    args['order_by'] = order_by
    args['order_direction'] = order_direction

    return url_for(request.endpoint, **args)