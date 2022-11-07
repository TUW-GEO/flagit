class Variables():
    """
    Class for flagging thresholds of soil moisture, accompanying ancillary observations and
    """
    ancillary_ta_lower = 0
    ancillary_ts_lower = 0
    ancillary_p_min = 0.2
    plateau_count = 0
    
    def low_boundary(self, var):
        """
        Lower threshold for quality control
        units:
        soil moisture : m³/m³
        soil temperature, air temperture, surface temperature : degree Celsius
        precipitation, snow water equivalent, snow depth : mm
        soil suction : kPa

        Parameters:
        -----------
        var : string
        variable name (some examples are:  soil_moisture, soil_temperature, snow_water_equivalent)
        """
        low_boundary_dict = {'soil_moisture': 0, 'soil_temperature': -60, 'air_temperature': -60, 'precipitation': 0,
                          'surface_temperature': -60, 'soil_suction': 0, 'snow_water_equivalent': 0, 'snow_depth':
                          0}
        return low_boundary_dict[var]
        
    def hi_boundary(self, var):
        """
        Upper threshold for quality control
        units:
        soil moisture : m³/m³
        soil temperature, air temperture, surface temperature : degree Celsius
        precipitation, snow water equivalent, snow depth : mm
        soil suction : kPa

        Parameters:
        -----------
        var : string
        variable name (some examples are:  soil_moisture, soil_temperature, snow_water_equivalent)
        """
        hi_boundary_dict = {'soil_moisture': 60, 'soil_temperature': 60, 'air_temperature': 60, 'precipitation': 100,
                          'surface_temperature': 60, 'soil_suction': 2500, 'snow_water_equivalent': 10000, 
                            'snow_depth': 10000}
        return hi_boundary_dict[var]
        
