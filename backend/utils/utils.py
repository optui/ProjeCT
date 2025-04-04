import os
from pathlib import Path
from fastapi import HTTPException, status
import opengate as gate
from backend.models import Source
from backend.repositories.simulation_repository import SimulationRepository
from backend.repositories.source_repository import SourceRepository

UNIT_MAP = {
    "nm": gate.g4_units.nm,
    "mm": gate.g4_units.mm,
    "cm": gate.g4_units.cm,
    "m": gate.g4_units.m,
    "keV": gate.g4_units.keV,
    "Bq": gate.g4_units.Bq,
    "eV": gate.g4_units.eV,
    "MeV": gate.g4_units.MeV,
    "sec": gate.g4_units.second
}

def handle_directory_rename(current, new_name: str) -> None:
    old_dir = current.output_dir
    new_dir = f"./output/{new_name}"

    if old_dir != new_dir and os.path.exists(old_dir):
        os.rename(old_dir, new_dir)
        old_json_path = os.path.join(new_dir, current.json_archive_filename)
        if os.path.exists(old_json_path):
            os.remove(old_json_path)

def to_json_file(sim) -> None:
    run_intervals = compute_run_timing_intervals(sim.num_runs, sim.run_len)
    gate_sim = gate.Simulation(
        name=sim.name,
        output_dir=sim.output_dir,
        json_archive_filename=sim.json_archive_filename,
        run_timing_intervals=run_intervals,
    )
    gate_sim.to_json_file()

def compute_run_timing_intervals(num_runs: int, run_len: float) -> list[list[float]]:
    """
    Compute a list of run timing intervals for GATE simulations.

    Args:
        num_runs (int): Number of run intervals to compute.
        run_len (float): Length of each run in seconds.

    Returns:
        List[List[float]]: A list of [start, end] time intervals in GATE time units.
    """
    return [[i * run_len * UNIT_MAP["sec"], (i + 1) * run_len * UNIT_MAP["sec"]] for i in range(num_runs)]

async def get_gate_simulation_without_sources(
    id: int, 
    simulation_repository: SimulationRepository,
) -> gate.Simulation:
    simulation = await simulation_repository.read(id)
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation with id {id} not found",
        )

    path = Path(simulation.output_dir) / simulation.json_archive_filename
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation configuration file not found",
        )

    sim = gate.Simulation()
    sim.from_json_file(str(path))
    return sim

async def get_gate_simulation(
    id: int, 
    simulation_repository: SimulationRepository,
    source_repository: SourceRepository
) -> gate.Simulation:
    simulation = await simulation_repository.read(id)
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation with id {id} not found",
        )

    path = Path(simulation.output_dir) / simulation.json_archive_filename
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation configuration file not found",
        )

    sim = gate.Simulation()
    sim.from_json_file(str(path))
    
    sources: list[Source] = await source_repository.read_sources(id)
    for src in sources:
        gate_source = sim.add_source("GenericSource", src.name)
        gate_source.particle = src.particle

        # Reconstruct position
        pos = src.position
        pos_factor = UNIT_MAP[pos["unit"]]
        if pos["type"] == "box":
            gate_source.position.type = "box"
            gate_source.position.size = [s * pos_factor for s in pos["size"]]
            gate_source.position.translation = [t * pos_factor for t in pos["translation"]]

        # Reconstruct direction
        direction = src.direction
        if direction["type"] == "focused":
            gate_source.direction.type = "focused"
            gate_source.direction.focus_point = [fp * pos_factor for fp in direction["focus_point"]]

        # Reconstruct energy
        energy = src.energy
        energy_factor = UNIT_MAP[energy["unit"]]
        if energy["type"] == "mono":
            gate_source.energy.type = "mono"
            gate_source.energy.mono = energy["mono"] * energy_factor

        # Reconstruct activity/n
        if src.activity:
            activity_factor = UNIT_MAP.get(src.activity_unit, 1)
            gate_source.activity = src.activity * activity_factor
        if src.n:
            gate_source.n = src.n
    
    return sim
