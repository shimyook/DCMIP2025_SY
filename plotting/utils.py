import matplotlib.colors as colors
import numpy as np
import xarray as xr

# A function to perform interpolation to a constant altitude

def z_interp(h, field_vals_all, lon, lat, z_val):
    field_vals = np.zeros((len(lat), len(lon)))
    for i in np.arange(len(lat)):
        for j in np.arange(len(lon)):
            if h[-1, i, j] > z_val:
                # This value is inside the topography
                field_vals[i, j] = np.nan
                # field_vals[i, j] = field_vals_all[-1,i,j]
            else:
                # Find indices either side of this value
                low_idx = np.where(h[:, i, j] < z_val)[0][0]
                high_idx = np.where(h[:, i, j] > z_val)[0][-1]

                # Compute weightings
                weight_low = (z_val - h[low_idx, i, j])/(h[high_idx, i, j] - h[low_idx, i, j])
                weight_high = 1. - weight_low
    
                # Compute and store value
                field_vals[i, j] = weight_low*field_vals_all[low_idx, i, j] + weight_high * field_vals_all[high_idx, i, j]
    return field_vals

# interpolates u and v at the same time
def z_interp_uv(h, u_field, v_field, lon, lat, z_val):
    field_vals = np.zeros((2, len(lat), len(lon)))
    for i in np.arange(len(lat)):
        for j in np.arange(len(lon)):
            if h[-1, i, j] > z_val:
                # This value is inside the topography
                field_vals[0, i, j] = np.nan
                field_vals[1, i, j] = np.nan
                # field_vals[0, i, j] = u_field[-1, i, j]
                # field_vals[1, i, j] = v_field[-1, i, j]
            else:
                # Find indices either side of this value
                low_idx = np.where(h[:, i, j] < z_val)[0][0]
                high_idx = np.where(h[:, i, j] > z_val)[0][-1]

                # Compute weightings
                weight_low = (z_val - h[low_idx, i, j])/(h[high_idx, i, j] - h[low_idx, i, j])
                weight_high = 1. - weight_low

                # Compute and store value
                field_vals[0, i, j] = weight_low*u_field[low_idx, i, j] + weight_high * u_field[high_idx, i, j]
                field_vals[1, i, j] = weight_low*v_field[low_idx, i, j] + weight_high * v_field[high_idx, i, j]
    return field_vals

def z_interp_w_hydrostatic(nc, time, lon, lat, z_val):
    h = nc['Z3'][time, :, lat, lon]
    try:
        q = nc['Q'][time, :, lat, lon]
    except:
        q = 0
        qval = 0
    T_field = nc['T'][time, :, lat, lon]
    hyam = nc['hyam']
    hybm = nc['hybm']
    PS = nc['PS'][time, lat, lon]
    omega_field = nc['OMEGA'][time, :, lat, lon]
    field_vals = np.zeros((len(lat), len(lon)))
    for i in np.arange(len(lat)):
        for j in np.arange(len(lon)):
            if h[-1, i, j] > z_val:
                # This value is inside the topography
                field_vals[i, j] = np.nan
            else:
                # Find indices either side of this value
                low_idx = np.where(h[:, i, j] < z_val)[0][0]
                high_idx = np.where(h[:, i, j] > z_val)[0][-1]

                # Compute weightings
                weight_low = (z_val - h[low_idx, i, j])/(h[high_idx, i, j] - h[low_idx, i, j])
                weight_high = 1. - weight_low

                # Compute and store value
                if (q != 0):
                    qval = weight_low * q[low_idx, i, j] + weight_high * q[high_idx, i, j]
                T = weight_low * T_field[low_idx, i, j] + weight_high * T_field[high_idx, i, j]
                p1 = hyam[low_idx]*1e5 + hybm[low_idx]*PS[i, j]
                p2 = hyam[high_idx]*1e5 + hybm[high_idx]*PS[i, j]
                P = weight_low * p1 + weight_high * p2
                Tv = T * (1.0 + 0.608 * qval)
                rho = P / (287.0 * Tv)
                omega = weight_low * omega_field[low_idx, i, j] + weight_high * omega_field[high_idx, i, j]
                field_vals[i, j] = -omega/(rho * 9.81)
    return field_vals

def z_interp_w_nonhydro(nc, time, lon, lat, z_val):
    h = nc['Z3'][time, :, lat, lon]
    try:
        q = nc['Q'][time, :, lat, lon]
        qval = 1
    except:
        q = 0
        qval = 0
    T_field = nc['T'][time, :, lat, lon]
    hyam = nc['hyam']
    hybm = nc['hybm']
    P_field = nc['PMID'][time, :, lat, lon]
    omega_field = nc['OMEGA'][time, :, lat, lon]
    field_vals = np.zeros((len(lat), len(lon)))
    for i in np.arange(len(lat)):
        for j in np.arange(len(lon)):
            if h[-1, i, j] > z_val:
                # This value is inside the topography
                field_vals[i, j] = np.nan
            else:
                # Find indices either side of this value
                low_idx = np.where(h[:, i, j] < z_val)[0][0]
                high_idx = np.where(h[:, i, j] > z_val)[0][-1]

                # Compute weightings
                weight_low = (z_val - h[low_idx, i, j])/(h[high_idx, i, j] - h[low_idx, i, j])
                weight_high = 1. - weight_low

                # Compute and store value
                if (qval != 0):
                    qval = weight_low * q[low_idx, i, j] + weight_high * q[high_idx, i, j]
                T = weight_low * T_field[low_idx, i, j] + weight_high * T_field[high_idx, i, j]
                P = weight_low * P_field[low_idx, i, j] + weight_high * P_field[high_idx, i, j]
                Tv = T * (1.0 + 0.608 * qval)
                rho = P / (287.0 * Tv)
                omega = weight_low * omega_field[low_idx, i, j] + weight_high * omega_field[high_idx, i, j]
                field_vals[i, j] = -omega/(rho * 9.81)
    return field_vals

def z_interp_xr(ds, t_idxs, z_levs, lon_inds):
    out = np.zeros((len(t_idxs), len(z_levs), len(lon_inds)))
    for i in range(len(t_idxs)):
        for j in range(len(lon_inds)):
            slice = ds.isel(time=t_idxs[i], lon=lon_inds[j])
            out[i, :, j] = slice.set_index(lev='Z3').interp(lev=z_levs).to_dataarray().data
    return out

def z_interp_divvor(divvor, t_idxs, z_levs, lon_inds):
    out = np.zeros((len(t_idxs), len(z_levs), len(lon_inds)))
    for i in range(len(t_idxs)):
        for j in range(len(lon_inds)):
            slice = divvor.isel(time=i, lon=j)
            out[i, :, j] = slice.set_index(lev='Z3').interp(lev=z_levs).to_dataarray().data
    return out


class MidpointNormalize(colors.Normalize):  # a class for the colorbar normalization
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        v_ext = np.max([np.abs(self.vmin), np.abs(self.vmax)])
        x, y = [-v_ext, self.midpoint, v_ext], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))