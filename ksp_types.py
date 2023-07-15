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
    iSituation: int
    fWeight: float
    fThrustMax: float
    fVerticalSpeed: float
    fForwardSpeed: float
    fLateralSpeed: float
    fPitchSpeed: float
    fPitchTorqueMax: float
    fPitchMomentOfInertia: float
    fYawSpeed: float
    fYawTorqueMax: float
    fYawMomentOfInertia: float

@dataclass
class VesselFlightControl:
    bIsInputValid: bool
    fThrottle: float
    fPitch: float
    fYaw: float
