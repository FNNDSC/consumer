from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from app.controllers.association import add_rule,get_rules,get_analyses
from app.models.association import PACSqueryCore, Association, AssociationList

router = APIRouter()

@router.post(
    "",
    status_code=201,
    response_description="new rule added successfully",
    summary="Add new `Association` rule.",
)
async def add_new_association(association_data: Association = Body(...)) -> dict:
    association_data = jsonable_encoder(association_data)
    new_association = add_rule(association_data)
    return new_association

@router.get(
    "",
    status_code=200,
    response_description="Association fetched successfully",
    summary="Retrieve existing association.",
)
async def get_all_association() -> AssociationList:
    return get_rules()

@router.post(
    "/analyses",
    status_code=200,
    response_description="Analyses fetched successfully",
    summary="Retrieve all matching analyses",
)
async def get_matching_analyses(query: PACSqueryCore) -> list[str]:
    return get_analyses(query)