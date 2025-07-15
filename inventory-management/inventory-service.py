
from typing import Dict, Literal

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Used Fastapi for its speed. 
app = FastAPI(
    title="Inventory Management API",
    description="Simple inventory management system for t-shirts and pants",
    version="1.0.0"
)

# In memory storage : Dictionary to hold inventory counts and some random values to start with.
inventory_store: Dict[str, int] = {
    "tshirts": 20,
    "pants": 15
}

# Pydantic models: Used for request and response validation
class InventoryResponse(BaseModel):
    tshirts: int = Field(ge=0, description="Number of t-shirts in stock")
    pants: int = Field(ge=0, description="Number of pants in stock")

class InventoryUpdateRequest(BaseModel):
    item: Literal["tshirts", "pants"] = Field(description="Item to update")
    change: int = Field(description="Change in quantity (positive for add, negative for remove)")

class ErrorResponse(BaseModel):
    error: str
    message: str

@app.get("/")
async def root():
    """Root endpoint with basic service info"""
    return {
        "service": "Inventory Management API",
        "version": "1.0.0",
        "endpoints": {
            "inventory": "/inventory",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/inventory", response_model=InventoryResponse)
async def get_inventory():
    """Get current inventory counts for all items"""
    return InventoryResponse(
        tshirts=inventory_store["tshirts"],
        pants=inventory_store["pants"]
    )

@app.post("/inventory", response_model=InventoryResponse)
async def update_inventory(request: InventoryUpdateRequest):
    """Update inventory count for a specific item"""
    
    # Check
    if request.item not in inventory_store:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid item: {request.item}. Must be 'tshirts' or 'pants'"
        )
    
    # new quantity
    current_quantity = inventory_store[request.item]
    new_quantity = current_quantity + request.change
      
    # Validate that quantity doesn't go negative
    if new_quantity < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reduce {request.item} by {abs(request.change)}. Only {current_quantity} available."
        )
    
    # Update inventory
    inventory_store[request.item] = new_quantity
    
    # Return updated inventory
    return InventoryResponse(
        tshirts=inventory_store["tshirts"],
        pants=inventory_store["pants"]
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "inventory_items": len(inventory_store)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


