from fastapi import APIRouter, status
from typing import List

from backend.schemas.api import MessageResponse
from backend.schemas.volume import (
    VolumeCreate,
    VolumeRead,
    VolumeUpdate,
)
from backend.api.dependencies import VolumeServiceDep

router = APIRouter(tags=["Volumes"])


@router.get(
    "/{simulation_id}/volumes",
    response_model=List[str]
)
async def read_volumes(service: VolumeServiceDep, simulation_id: int):
    return await service.read_volumes(simulation_id)


@router.post(
    "/{simulation_id}/volumes",
    response_model=VolumeRead,
    status_code=status.HTTP_201_CREATED
)
async def create_volume(
    service: VolumeServiceDep, simulation_id: int, volume: VolumeCreate
):
    return await service.create_volume(simulation_id, volume)


@router.get(
    "/{simulation_id}/volumes/{name}",
    response_model=VolumeRead,
    responses={404: {"model": MessageResponse}}
)
async def read_volume(service: VolumeServiceDep, simulation_id: int, name: str):
    return await service.read_volume(simulation_id, name)


@router.put(
    "/{simulation_id}/volumes/{name}",
    response_model=VolumeRead
)
async def update_volume(
    service: VolumeServiceDep, simulation_id: int, name: str, volume: VolumeUpdate
):
    return await service.update_volume(simulation_id, name, volume)


@router.delete("/{simulation_id}/volumes/{name}", response_model=MessageResponse)
async def delete_volume(service: VolumeServiceDep, simulation_id: int, name: str):
    return await service.delete_volume(simulation_id, name)
