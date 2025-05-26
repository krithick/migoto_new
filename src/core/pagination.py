from typing import TypeVar, Generic, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResult(BaseModel, Generic[T]):
    """Paginated result container"""
    items: List[T]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool
    
    @property
    def pages(self) -> int:
        """Total number of pages"""
        return (self.total + self.limit - 1) // self.limit if self.limit > 0 else 0
    
    @property
    def current_page(self) -> int:
        """Current page number (1-based)"""
        return (self.skip // self.limit) + 1 if self.limit > 0 else 1

async def paginate(
    query_func,
    skip: int = 0,
    limit: int = 100,
    **kwargs
) -> PaginatedResult:
    """Helper to paginate query results"""
    # Get items
    items = await query_func(skip=skip, limit=limit, **kwargs)
    
    # Get total count
    if hasattr(query_func, 'count'):
        total = await query_func.count(**kwargs)
    else:
        total = len(items)
    
    return PaginatedResult(
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0
    )
