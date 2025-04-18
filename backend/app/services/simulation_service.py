import os
import shutil
from fastapi import HTTPException
from app.repositories.simulation_repository import SimulationRepository
from app.repositories.source_repository import SourceRepository
from app.schemas.api import MessageResponse
from app.schemas.simulation import SimulationCreate, SimulationRead, SimulationUpdate
from app.utils.utils import get_gate_sim, handle_directory_rename, to_json_file
import opengate as gate


class SimulationService:
    def __init__(self, simulation_repository: SimulationRepository):
        self.sim_repo = simulation_repository
        
    async def get_gate_sim_without_sources(self, sim_id: int) -> gate.Simulation:
        sim = await self.read_simulation(sim_id)
        gate_sim = gate.Simulation()
        gate_sim.from_json_file(f"{sim.output_dir}/{sim.json_archive_filename}")
        return gate_sim

    async def create_simulation(self, sim_create: SimulationCreate) -> SimulationRead:
        sim: SimulationRead = await self.sim_repo.create(sim_create)
        to_json_file(sim)
        return sim

    async def read_simulations(self) -> list[SimulationRead]:
        return await self.sim_repo.read_all()

    async def read_simulation(self, id: int) -> SimulationRead:
        sim: SimulationRead | None = await self.sim_repo.read(id)
        if not sim:
            raise HTTPException(status_code=404, detail=f"Simulation with id {id} not found")
        return sim

    async def update_simulation(self, id: int, sim_update: SimulationUpdate) -> SimulationRead:
        existing_sim: SimulationRead = await self.read_simulation(id)
        handle_directory_rename(existing_sim, sim_update.name)
        updated_sim = await self.sim_repo.update(id, sim_update)
        to_json_file(updated_sim)
        return updated_sim

    async def delete_simulation(self, id: int) -> MessageResponse:
        sim: SimulationRead | None = await self.sim_repo.delete(id)
        if not sim:
            raise HTTPException(status_code=404, detail=f"Simulation with id {id} not found")
        if os.path.exists(sim.output_dir):
            shutil.rmtree(sim.output_dir)
        return {"message": "Simulation deleted successfully"}

    async def import_simulation(self, id: int) -> MessageResponse:
        raise HTTPException(status_code=501, detail="Import functionality not implemented yet")

    async def export_simulation(self, id: int) -> MessageResponse:
        raise HTTPException(status_code=501, detail="Export functionality not implemented yet")

    async def view_simulation(self, id: int, source_repository: SourceRepository) -> MessageResponse:
        gate_sim = await get_gate_sim(id, self.sim_repo, source_repository)
        gate_sim.visu = True
        gate_sim.run(start_new_process=True)
        return {"message": "Simulation visualization ended"}

    async def run_simulation(self, id: int, source_repository: SourceRepository) -> MessageResponse:
        gate_sim = await get_gate_sim(id, self.sim_repo, source_repository)
        gate_sim.visu = False
        gate_sim.run(start_new_process=True)
        return {"message": "Simulation finished running"}
