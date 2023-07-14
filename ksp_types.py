from dataclasses import dataclass

#
# Types
#
@dataclass
class VesselAttitude:
    bIsDataValid: bool
    fHeading: float
    fPitch: float
    fRoll: float

@dataclass
class VesselOrbitalParameters:
    bIsDataValid: bool
    sCelestialBodyName: str
    fCelestialBodyMass: float
    fPeriod: float
    fTimeToApoapsis: float
    fTimeToPeriapsis: float

@dataclass
class VesselResources:
    bIsDataValid: bool
    fWater: float
    fWaterMax: float
    fFood: float
    fFoodMax: float
    fOxygen: float
    fOxygenMax: float
    fAtmo: float
    fAtmoMax: float
    fWasteAtmo: float
    fWasteAtmoMax: float

@dataclass
class VesselFlightState:
    bIsDataValid: bool
    fThrustMax: float
    fVerticalSpeed: float
    fWeight: float

@dataclass
class VesselFlightControl:
    bIsInputValid: bool
    fThrottle: float
