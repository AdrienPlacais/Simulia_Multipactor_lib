'# PS Version: Version 2023.5 - Jun 08 2023 - ACIS 32.0.1 -

'# length = mm
'# frequency = GHz
'# time = ns
'# frequency range: fmin = 10 fmax = 15
'# created = '[VERSION]2023.5|32.0.1|20230608[/VERSION]


'@ change solver type

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
ChangeSolverType "HF Frequency Domain"

'@ define frequency range

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
Solver.FrequencyRange "10", "15"

'@ define units

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With Units 
     .SetUnit "Length", "mm"
     .SetUnit "Temperature", "K"
     .SetUnit "Voltage", "V"
     .SetUnit "Current", "A"
     .SetUnit "Resistance", "Ohm"
     .SetUnit "Conductance", "S"
     .SetUnit "Capacitance", "pF"
     .SetUnit "Inductance", "nH"
     .SetUnit "Frequency", "GHz"
     .SetUnit "Time", "ns"
     .SetResultUnit "frequency", "frequency", "" 
End With

'@ new component: component1

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
Component.New "component1"

'@ define brick: component1:waveguide

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With Brick
     .Reset 
     .Name "waveguide" 
     .Component "component1" 
     .Material "PEC" 
     .Xrange "-width/2-thickness", "width/2+thickness" 
     .Yrange "-thickness", "thickness+height" 
     .Zrange "-length/2", "length/2" 
     .Create
End With

'@ define brick: component1:vacuum

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With Brick
     .Reset 
     .Name "vacuum" 
     .Component "component1" 
     .Material "Vacuum" 
     .Xrange "-width/2", "width/2" 
     .Yrange "0", "height" 
     .Zrange "-length/2", "length/2" 
     .Create
End With

'@ boolean insert shapes: component1:waveguide, component1:vacuum

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
Solid.Insert "component1:waveguide", "component1:vacuum"

'@ pick face

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
Pick.PickFaceFromId "component1:vacuum", "2"

'@ define port: 1

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With Port 
     .Reset 
     .PortNumber "1" 
     .Label ""
     .Folder ""
     .NumberOfModes "1"
     .AdjustPolarization "False"
     .PolarizationAngle "0.0"
     .ReferencePlaneDistance "0"
     .TextSize "50"
     .TextMaxLimit "0"
     .Coordinates "Picks"
     .Orientation "positive"
     .PortOnBound "False"
     .ClipPickedPortToBound "False"
     .Xrange "-9.525", "9.525"
     .Yrange "0", "9.525"
     .Zrange "-15", "-15"
     .XrangeAdd "0.0", "0.0"
     .YrangeAdd "0.0", "0.0"
     .ZrangeAdd "0.0", "0.0"
     .SingleEnded "False"
     .WaveguideMonitor "False"
     .Create 
End With

'@ pick face

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
Pick.PickFaceFromId "component1:vacuum", "1"

'@ define port: 2

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With Port 
     .Reset 
     .PortNumber "2" 
     .Label ""
     .Folder ""
     .NumberOfModes "1"
     .AdjustPolarization "False"
     .PolarizationAngle "0.0"
     .ReferencePlaneDistance "0"
     .TextSize "50"
     .TextMaxLimit "0"
     .Coordinates "Picks"
     .Orientation "positive"
     .PortOnBound "False"
     .ClipPickedPortToBound "False"
     .Xrange "-9.525", "9.525"
     .Yrange "0", "9.525"
     .Zrange "15", "15"
     .XrangeAdd "0.0", "0.0"
     .YrangeAdd "0.0", "0.0"
     .ZrangeAdd "0.0", "0.0"
     .SingleEnded "False"
     .WaveguideMonitor "False"
     .Create 
End With

'@ define frequency domain solver parameters

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
Mesh.SetCreator "High Frequency" 

With FDSolver
     .Reset 
     .SetMethod "Tetrahedral", "General purpose" 
     .OrderTet "Second" 
     .OrderSrf "First" 
     .Stimulation "All", "All" 
     .ResetExcitationList 
     .AutoNormImpedance "False" 
     .NormingImpedance "50" 
     .ModesOnly "False" 
     .ConsiderPortLossesTet "True" 
     .SetShieldAllPorts "False" 
     .AccuracyHex "1e-6" 
     .AccuracyTet "1e-4" 
     .AccuracySrf "1e-3" 
     .LimitIterations "False" 
     .MaxIterations "0" 
     .SetCalcBlockExcitationsInParallel "True", "True", "" 
     .StoreAllResults "False" 
     .StoreResultsInCache "False" 
     .UseHelmholtzEquation "True" 
     .LowFrequencyStabilization "True" 
     .Type "Auto" 
     .MeshAdaptionHex "False" 
     .MeshAdaptionTet "True" 
     .AcceleratedRestart "True" 
     .FreqDistAdaptMode "Distributed" 
     .NewIterativeSolver "True" 
     .TDCompatibleMaterials "False" 
     .ExtrudeOpenBC "False" 
     .SetOpenBCTypeHex "Default" 
     .SetOpenBCTypeTet "Default" 
     .AddMonitorSamples "True" 
     .CalcPowerLoss "True" 
     .CalcPowerLossPerComponent "False" 
     .StoreSolutionCoefficients "True" 
     .UseDoublePrecision "False" 
     .UseDoublePrecision_ML "True" 
     .MixedOrderSrf "False" 
     .MixedOrderTet "False" 
     .PreconditionerAccuracyIntEq "0.15" 
     .MLFMMAccuracy "Default" 
     .MinMLFMMBoxSize "0.3" 
     .UseCFIEForCPECIntEq "True" 
     .UseEnhancedCFIE2 "True" 
     .UseFastRCSSweepIntEq "false" 
     .UseSensitivityAnalysis "False" 
     .UseEnhancedNFSImprint "False" 
     .UseFastDirectFFCalc "False" 
     .RemoveAllStopCriteria "Hex"
     .AddStopCriterion "All S-Parameters", "0.01", "2", "Hex", "True"
     .AddStopCriterion "Reflection S-Parameters", "0.01", "2", "Hex", "False"
     .AddStopCriterion "Transmission S-Parameters", "0.01", "2", "Hex", "False"
     .RemoveAllStopCriteria "Tet"
     .AddStopCriterion "All S-Parameters", "0.01", "2", "Tet", "True"
     .AddStopCriterion "Reflection S-Parameters", "0.01", "2", "Tet", "False"
     .AddStopCriterion "Transmission S-Parameters", "0.01", "2", "Tet", "False"
     .AddStopCriterion "All Probes", "0.05", "2", "Tet", "True"
     .RemoveAllStopCriteria "Srf"
     .AddStopCriterion "All S-Parameters", "0.01", "2", "Srf", "True"
     .AddStopCriterion "Reflection S-Parameters", "0.01", "2", "Srf", "False"
     .AddStopCriterion "Transmission S-Parameters", "0.01", "2", "Srf", "False"
     .SweepMinimumSamples "3" 
     .SetNumberOfResultDataSamples "1001" 
     .SetResultDataSamplingMode "Automatic" 
     .SweepWeightEvanescent "1.0" 
     .AccuracyROM "1e-4" 
     .AddSampleInterval "", "", "1", "Automatic", "True" 
     .AddSampleInterval "", "", "", "Automatic", "False" 
     .MPIParallelization "False"
     .UseDistributedComputing "False"
     .NetworkComputingStrategy "RunRemote"
     .NetworkComputingJobCount "3"
     .UseParallelization "True"
     .MaxCPUs "1024"
     .MaximumNumberOfCPUDevices "2"
End With

With IESolver
     .Reset 
     .UseFastFrequencySweep "True" 
     .UseIEGroundPlane "False" 
     .SetRealGroundMaterialName "" 
     .CalcFarFieldInRealGround "False" 
     .RealGroundModelType "Auto" 
     .PreconditionerType "Auto" 
     .ExtendThinWireModelByWireNubs "False" 
     .ExtraPreconditioning "False" 
End With

With IESolver
     .SetFMMFFCalcStopLevel "0" 
     .SetFMMFFCalcNumInterpPoints "6" 
     .UseFMMFarfieldCalc "True" 
     .SetCFIEAlpha "0.500000" 
     .LowFrequencyStabilization "False" 
     .LowFrequencyStabilizationML "True" 
     .Multilayer "False" 
     .SetiMoMACC_I "0.0001" 
     .SetiMoMACC_M "0.0001" 
     .DeembedExternalPorts "True" 
     .SetOpenBC_XY "True" 
     .OldRCSSweepDefintion "False" 
     .SetRCSOptimizationProperties "True", "100", "0.00001" 
     .SetAccuracySetting "Custom" 
     .CalculateSParaforFieldsources "True" 
     .ModeTrackingCMA "True" 
     .NumberOfModesCMA "3" 
     .StartFrequencyCMA "-1.0" 
     .SetAccuracySettingCMA "Default" 
     .FrequencySamplesCMA "0" 
     .SetMemSettingCMA "Auto" 
     .CalculateModalWeightingCoefficientsCMA "True" 
     .DetectThinDielectrics "True" 
End With

'@ change problem type

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
ChangeProblemType "PIC Solver"

'@ define material: SEE - Cu as received

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With Material 
     .Reset 
     .Name "SEE - Cu as received"
     .Folder ""
     .Rho "0.0"
     .ThermalType "Normal"
     .ThermalConductivity "0"
     .SpecificHeat "0", "J/K/kg"
     .DynamicViscosity "0"
     .UseEmissivity "True"
     .Emissivity "0"
     .MetabolicRate "0.0"
     .VoxelConvection "0.0"
     .BloodFlow "0"
     .MechanicsType "Unused"
     .IntrinsicCarrierDensity "0"
     .FrqType "all"
     .Type "Pec"
     .MaterialUnit "Frequency", "GHz"
     .MaterialUnit "Geometry", "mm"
     .MaterialUnit "Time", "ns"
     .MaterialUnit "Temperature", "Kelvin"
     .Epsilon "1.0"
     .Mu "1"
     .ReferenceCoordSystem "Global"
     .CoordSystemType "Cartesian"
     .NLAnisotropy "False"
     .NLAStackingFactor "1"
     .NLADirectionX "1"
     .NLADirectionY "0"
     .NLADirectionZ "0"
     .ParticleProperty "SecondaryEmission"
     .SeModel "Import"
     .SePlot1D "True", "0", "100", "0", "1000"
     .SeImportSettings "\\lpscdata12.in2p3.fr\data11-pole\placais\Documents\electron_emission_data\measured_TEEY_Cu_2_as-received.txt", "7.5"
     .SeImportData "0", "0"
     .SeImportData "10", "0.696"
     .SeImportData "30", "1.1"
     .SeImportData "50", "1.364"
     .SeImportData "70", "1.605"
     .SeImportData "90", "1.754"
     .SeImportData "110", "1.895"
     .SeImportData "130", "1.979"
     .SeImportData "150", "2.021"
     .SeImportData "170", "2.115"
     .SeImportData "190", "2.153"
     .SeImportData "210", "2.185"
     .SeImportData "230", "2.221"
     .SeImportData "250", "2.237"
     .SeImportData "270", "2.234"
     .SeImportData "290", "2.221"
     .SeImportData "310", "2.208"
     .SeImportData "330", "2.201"
     .SeImportData "350", "2.193"
     .SeImportData "370", "2.17"
     .SeImportData "390", "2.199"
     .SeImportData "410", "2.181"
     .SeImportData "430", "2.182"
     .SeImportData "450", "2.145"
     .SeImportData "470", "2.15"
     .SeImportData "490", "2.121"
     .SeImportData "510", "2.097"
     .SeImportData "530", "2.102"
     .SeImportData "550", "2.077"
     .SeImportData "570", "2.075"
     .SeImportData "590", "2.039"
     .SeImportData "610", "2.047"
     .SeImportData "630", "2.032"
     .SeImportData "650", "2.027"
     .SeImportData "670", "2.007"
     .SeImportData "690", "1.998"
     .SeImportData "710", "2.001"
     .SeImportData "730", "1.982"
     .SeImportData "750", "1.969"
     .SeImportData "770", "1.936"
     .SeImportData "790", "1.94"
     .SeImportData "810", "1.931"
     .SeImportData "830", "1.918"
     .SeImportData "850", "1.921"
     .SeImportData "870", "1.909"
     .SeImportData "890", "1.89"
     .SeImportData "910", "1.884"
     .SeImportData "930", "1.88"
     .SeImportData "950", "1.856"
     .SeImportData "970", "1.875"
     .SeImportData "990", "1.838"
     .Colour "0", "1", "1" 
     .Wireframe "False" 
     .Reflection "False" 
     .Allowoutline "True" 
     .Transparentoutline "False" 
     .Transparency "0" 
     .Create
End With

'@ define material colour: SEE - Cu as received

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With Material 
     .Name "SEE - Cu as received"
     .Folder ""
     .Colour "0", "1", "1" 
     .Wireframe "False" 
     .Reflection "False" 
     .Allowoutline "True" 
     .Transparentoutline "False" 
     .Transparency "0" 
     .ChangeColour 
End With

'@ change material: component1:waveguide to: SEE - Cu as received

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
Solid.ChangeMaterial "component1:waveguide", "SEE - Cu as received"

'@ define particle source: particle1

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With ParticleSource
     .Reset
     .Name "particle1"
     .ParticleType "electron"
     .Charge "-1.602176565e-19"
     .Mass "9.109382910e-31"
     .SourceType "Volume"
     .VolumeSourceDistributionMethod "0"
     .AddFace "component1:vacuum", "2"
     .PICEmissionModel "Maxwellian"
     .MaxwellParticleDensity "1e+10"
     .MaxwellNumMacroParticles "1000"
     .MaxwellSeedRNG "False", "10"
     .MaxwellTimeSettings "False", "1", "0.0", "2*T_rf"
     .MaxwellTemperatureSettings "1.0", "1.0", "1.0", "100.0"
     .MaxwellDriftSettings "False", "0.0", "0.0", "0.0"
     .Create
End With

'@ define pic solver parameters

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
Mesh.SetCreator "PIC" 

With PICSolver
     .ConsiderEStaticField "False"
     .EStaticFactor "1.0"
     .ConsiderMStaticField "False"
     .MStaticFactor "1.0"
     .ConsiderAnalyticPredefinedField "False"
     .AnalyticPredefinedFactor "1.0"
     .ConsiderExternalPredefinedField "True"
     .ExternalPredefinedFactor "sqr(power)"
     .StimulationPort "Selected"
     .StimulationMode "All"
     .SimulationTime "t_max"
     .CalculateModesOnly "False"
     .StoreTDResultsInCache "False"
End With

'@ set PBA version

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
Discretizer.PBAVersion "2023060823"

'@ define special pic solver parameters

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
'GENERAL
With Solver
     .TimeStepStabilityFactor "1.0"
     .RestartAfterInstabilityAbort "False"
     .AutomaticTimeSignalSampling "True"
     .ConsiderExcitationForFreqSamplingRate "False"
     .UseBroadBandPhaseShift "False"
     .SetBroadBandPhaseShiftLowerBoundFac "0.1"
     .SetPortShieldingType "NONE"
     .FrequencySamples "1001"
End With

'MATERIAL
With Solver
     .SurfaceImpedanceOrder "10"
     .ActivatePowerLoss1DMonitor "True"
     .PowerLoss1DMonitorPerSolid "False"
     .Use3DFieldMonitorForPowerLoss1DMonitor "True"
     .UseFarFieldMonitorForPowerLoss1DMonitor "False"
     .UseExtraFreqForPowerLoss1DMonitor "False"
     .ResetPowerLoss1DMonitorExtraFreq
     .SetDispNonLinearMaterialMonitor "False"
     .ActivateDispNonLinearMaterialMonitor "0.0",  "0.01",  "0.0",  "False"
     .SetTimePowerLossSIMaterialMonitor "False"
     .ActivateTimePowerLossSIMaterialMonitor "0.0",  "0.01",  "0.0",  "False"
     .SetTimePowerLossSIMaterialMonitorAverage "False"
     .SetTimePowerLossSIMaterialMonitorAverageRepPeriod "0.0"
     .TimePowerLossSIMaterialMonitorPerSolid "False"
     .ActivateSpaceMaterial3DMonitor "False"
     .Use3DFieldMonitorForSpaceMaterial3DMonitor "True"
     .UseExtraFreqForSpaceMaterial3DMonitor "False"
     .ResetSpaceMaterial3DMonitorExtraFreq
     .SetHFTDDispUpdateScheme "Automatic"
End With

'HEXAHEDRAL
With Solver
     .SetPMLType "CONVPML"
     .UseVariablePMLLayerSizeStandard "False"
     .KeepPMLDepthDuringMeshAdaptationWithVariablePMLLayerSize "False"
     .SetSubcycleState "Automatic"
     .NormalizeToReferenceSignal "False"
     .SetEnhancedPMLStabilization "Automatic"
     .DiscreteItemUpdate "Distributed"
End With

'WAVEGUIDE
With Solver
     .WaveguidePortGeneralized "True"
     .WaveguidePortModeTracking "False"
     .WaveguidePortROM "False"
     .AbsorbUnconsideredModeFields "Automatic"
     .SetModeFreqFactor "0.5"
     .AdaptivePortMeshing "False"
     .AccuracyAdaptivePortMeshing "1"
     .PassesAdaptivePortMeshing "4"
End With

With PICSolver
     .DisableCurrentComputation "True"
     .MinimumEmission "Current", "0.0", "0.0"
     .MultipactingSolverStop "True", "3", "0.25", "1.1"
     .ThermalCoupling "False", "True", "0.0", "0.0"
     .UseBBPortDecomposition "False"
     .SetVoltageWaveguidePort "1", "1", "False"
     .SetVoltageWaveguidePort "2", "1", "False"
End With

'@ create particle monitor on solid: component1:waveguide

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With ParticleMonitorOnSolid
     .Reset
     .Name "component1:waveguide"
     .EnableCollisionInfo "True"
     .EnableCurrent "False"
     .EnablePower "False"
     .EnableEnergyHistogram "True"
     .EnergyBinSize "1.0"
     .EnergyMin "0.0"
     .EnergyMax "1e3"
     .Create
End With

'@ predefined external field settings

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With PredefinedField
     .ResetExternalSettings
     .FieldType "External"
     .UseLocalCopyOnly "False"
     .UpdateLocalCopies "False"
     .ExternalFieldMur "1.0"
     .SetExternalField "True", "wr75.cst", "1.0", "0.0", "0", "True"
     .SetExternalFieldDescription "0", "<mesh:hex><filename:e-field (#0007)_1(1).m3d>"
     .SetExternalFieldSpaceShift "0", "0.0", "0.0", "0.0"
     .SetExternalFieldTimeSignal "0", "[Constant]"
     .SetExternalFieldTimeShift "0", "0.0"
     .SetExternalField "True", "wr75.cst", "1.0", "0.0", "1", "True"
     .SetExternalFieldDescription "1", "<mesh:hex><filename:h-field (#0007)_1(1).m3d>"
     .SetExternalFieldSpaceShift "1", "0.0", "0.0", "0.0"
     .SetExternalFieldTimeSignal "1", "[Constant]"
     .SetExternalFieldTimeShift "1", "0.0"
     .Create
End With

'@ define PIC Position Monitor: position  monitor 1

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With PSMonitor 
     .ResetType "particle3d" 
     .Name "position  monitor 1" 
     .Tstart "0.0" 
     .Tstep "position_monitor_time_step" 
     .Tend "0.0" 
     .UseTend "False" 
     .Create 
End With

'@ define boundaries

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With Boundary
     .Xmin "open"
     .Xmax "open"
     .Ymin "open"
     .Ymax "open"
     .Zmin "open"
     .Zmax "open"
     .Xsymmetry "none"
     .Ysymmetry "none"
     .Zsymmetry "none"
     .ApplyInAllDirections "True"
End With

'@ define special pic solver parameters

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
'GENERAL
With Solver
     .TimeStepStabilityFactor "1.0"
     .RestartAfterInstabilityAbort "False"
     .AutomaticTimeSignalSampling "True"
     .ConsiderExcitationForFreqSamplingRate "False"
     .UseBroadBandPhaseShift "False"
     .SetBroadBandPhaseShiftLowerBoundFac "0.1"
     .SetPortShieldingType "NONE"
     .FrequencySamples "1001"
End With

'MATERIAL
With Solver
     .SurfaceImpedanceOrder "10"
     .ActivatePowerLoss1DMonitor "True"
     .PowerLoss1DMonitorPerSolid "False"
     .Use3DFieldMonitorForPowerLoss1DMonitor "True"
     .UseFarFieldMonitorForPowerLoss1DMonitor "False"
     .UseExtraFreqForPowerLoss1DMonitor "False"
     .ResetPowerLoss1DMonitorExtraFreq
     .SetDispNonLinearMaterialMonitor "False"
     .ActivateDispNonLinearMaterialMonitor "0.0",  "0.01",  "0.0",  "False"
     .SetTimePowerLossSIMaterialMonitor "False"
     .ActivateTimePowerLossSIMaterialMonitor "0.0",  "0.01",  "0.0",  "False"
     .SetTimePowerLossSIMaterialMonitorAverage "False"
     .SetTimePowerLossSIMaterialMonitorAverageRepPeriod "0.0"
     .TimePowerLossSIMaterialMonitorPerSolid "False"
     .ActivateSpaceMaterial3DMonitor "False"
     .Use3DFieldMonitorForSpaceMaterial3DMonitor "True"
     .UseExtraFreqForSpaceMaterial3DMonitor "False"
     .ResetSpaceMaterial3DMonitorExtraFreq
     .SetHFTDDispUpdateScheme "Automatic"
End With

'HEXAHEDRAL
With Solver
     .SetPMLType "CONVPML"
     .UseVariablePMLLayerSizeStandard "False"
     .KeepPMLDepthDuringMeshAdaptationWithVariablePMLLayerSize "False"
     .SetSubcycleState "Automatic"
     .NormalizeToReferenceSignal "False"
     .SetEnhancedPMLStabilization "Automatic"
     .DiscreteItemUpdate "Distributed"
End With

'WAVEGUIDE
With Solver
     .WaveguidePortGeneralized "True"
     .WaveguidePortModeTracking "False"
     .WaveguidePortROM "False"
     .AbsorbUnconsideredModeFields "Automatic"
     .SetModeFreqFactor "0.5"
     .AdaptivePortMeshing "False"
     .AccuracyAdaptivePortMeshing "1"
     .PassesAdaptivePortMeshing "4"
End With

With PICSolver
     .DisableCurrentComputation "True"
     .MinimumEmission "Current", "0.0", "0.0"
     .MultipactingSolverStop "False", "5", "T_rf", "1.1"
     .ThermalCoupling "False", "True", "0.0", "0.0"
     .UseBBPortDecomposition "False"
End With

'@ predefined external field settings

'[VERSION]2023.5|32.0.1|20230608[/VERSION]
With PredefinedField
     .ResetExternalSettings
     .FieldType "External"
     .UseLocalCopyOnly "False"
     .UpdateLocalCopies "False"
     .ExternalFieldMur "1.0"
     .SetExternalField "True", "wr75.cst", "1.0", "0.0", "2", "True"
     .SetExternalFieldDescription "2", "<mesh:hex><filename:e-field (#0002)_1(1).m3d>"
     .SetExternalFieldSpaceShift "2", "0.0", "0.0", "0.0"
     .SetExternalFieldTimeSignal "2", "[Constant]"
     .SetExternalFieldTimeShift "2", "0.0"
     .SetExternalField "True", "wr75.cst", "1.0", "0.0", "3", "True"
     .SetExternalFieldDescription "3", "<mesh:hex><filename:h-field (#0002)_1(1).m3d>"
     .SetExternalFieldSpaceShift "3", "0.0", "0.0", "0.0"
     .SetExternalFieldTimeSignal "3", "[Constant]"
     .SetExternalFieldTimeShift "3", "0.0"
     .Create
End With

