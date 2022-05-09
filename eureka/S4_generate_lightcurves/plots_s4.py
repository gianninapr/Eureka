import numpy as np
import matplotlib.pyplot as plt


def binned_lightcurve(meta, lc, i):
    '''Plot each spectroscopic light curve. (Fig 4300)

    Parameters
    ----------
    meta:   MetaClass
        The metadata object.
    lc:     Xarray Dataset
        The Dataset object containing light curve and time data.
    i:  int
        The current bandpass number.

    Returns
    -------
    None
    '''
    plt.figure(int('43{}'.format(str(0).zfill(int(np.floor(np.log10(meta.nspecchan))+1)))), figsize=(8, 6))
    plt.clf()
    plt.suptitle(f"Bandpass {i}: %.3f - %.3f" % (lc.wave_low.values[i], lc.wave_hi.values[i]))
    ax = plt.subplot(111)
    time_modifier = np.floor(lc.time.values[0])
    # Normalized light curve
    norm_lcdata = lc['data'][i] / np.nan.median(lc['data'][i], axis=0)
    norm_lcerr = lc['err'][i] / np.nan.median(lc['data'][i], axis=0)
    plt.errorbar(lc.time - time_modifier, norm_lcdata, norm_lcerr, fmt='o', color=f'C{i}', mec=f'C{i}', alpha = 0.2)
    plt.text(0.05, 0.1, "MAD = " + str(np.round(1e6 * np.ma.median(np.abs(np.ediff1d(norm_lcdata))))) + " ppm",
             transform=ax.transAxes, color='k')
    plt.ylabel('Normalized Flux')
    time_units = lc.data.attrs['time_units']
    plt.xlabel(f'Time [{time_units} - {time_modifier}]')

    plt.subplots_adjust(left=0.10, right=0.95, bottom=0.10, top=0.90, hspace=0.20, wspace=0.3)
    plt.savefig(meta.outputdir + 'figs/Fig43{}-1D_LC.png'.format(str(i).zfill(int(np.floor(np.log10(meta.nspecchan))+1))))
    if not meta.hide_plots:
        plt.pause(0.2)

def drift1d(meta, spec):
    '''Plot the 1D drift/jitter results. (Fig 4100)

    Parameters
    ----------
    meta:   MetaClass
        The metadata object.
    spec:     Xarray Dataset
        The spectra object containing drift arrays.

    Returns
    -------
    None
    '''
    plt.figure(int('41{}'.format(str(0).zfill(int(np.floor(np.log10(meta.nspecchan))+1)))), figsize=(8, 4))
    plt.clf()
    plt.plot(np.arange(meta.n_int)[np.where(~spec.driftmask)], spec.drift1d[np.where(~spec.driftmask)], '.', label='Good Drift Points')
    plt.plot(np.arange(meta.n_int)[np.where(spec.driftmask)], spec.drift1d[np.where(spec.driftmask)], '.', label='Interpolated Drift Points')
    plt.ylabel('Spectrum Drift Along x')
    plt.xlabel('Frame Number')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig(meta.outputdir + 'figs/Fig41{}-Drift.png'.format(str(0).zfill(int(np.floor(np.log10(meta.nspecchan))+1))))
    if not meta.hide_plots:
        plt.pause(0.2)

def lc_driftcorr(meta, wave_1d, optspec):
    '''Plot a 2D light curve with drift correction. (Fig 4200)

    Parameters
    ----------
    meta:   MetaClass
        The metadata object.
    wave_1d:
        Wavelength array with trimmed edges depending on xwindow and ywindow which have been set in the S3 ecf
    optspec:
        The optimally extracted spectrum.

    Returns
    -------
    None
    '''
    plt.figure(int('42{}'.format(str(0).zfill(int(np.floor(np.log10(meta.nspecchan))+1)))), figsize=(8, 8))
    plt.clf()
    wmin = wave_1d.min()
    wmax = wave_1d.max()
    n_int, nx = optspec.shape
    vmin = 0.97
    vmax = 1.03
    normspec = optspec / np.ma.mean(optspec, axis=0)
    plt.imshow(normspec, origin='lower', aspect='auto', extent=[wmin, wmax, 0, n_int], vmin=vmin, vmax=vmax,
               cmap=plt.cm.RdYlBu_r)
    plt.title("MAD = " + str(np.round(meta.mad_s4, 0).astype(int)) + " ppm")
    if meta.nspecchan > 1:
        # Insert vertical dashed lines at spectroscopic channel edges
        secax = plt.gca().secondary_xaxis('top')
        xticks = np.unique(np.concatenate([meta.wave_low,meta.wave_hi]))
        secax.set_xticks(xticks, xticks, rotation=90)
        plt.vlines(xticks,0,n_int,'0.3','dashed')
    plt.ylabel('Integration Number')
    plt.xlabel(r'Wavelength ($\mu m$)')
    plt.colorbar(label='Normalized Flux')
    plt.tight_layout()
    plt.savefig(meta.outputdir + 'figs/Fig42{}-2D_LC.png'.format(str(0).zfill(int(np.floor(np.log10(meta.nspecchan))+1))))
    if meta.hide_plots:
        plt.close()
    else:
        plt.pause(0.2)
    return

def cc_spec(meta, ref_spec, fit_spec, n):
    '''Compare the spectrum used for cross-correlation with the current spectrum (Fig 4400).

    Parameters
    ----------
    meta:   MetaClass
        The metadata object.
    ref_spec:   ndarray (1D)
        The reference spectrum used for cross-correlation.
    fit_spec:   ndarray (1D)
        The extracted spectrum for the current integration.
    n:  int
        The current integration number.

    Returns
    -------
    None
    '''
    plt.figure(int('44{}'.format(str(0).zfill(int(np.floor(np.log10(meta.nspecchan))+1)))), figsize=(8, 8))
    plt.clf()
    plt.title(f'Cross Correlation - Spectrum {n}')
    nx = len(ref_spec)
    plt.plot(range(nx), ref_spec, '-', label='Reference Spectrum')
    plt.plot(range(meta.drift_range,nx-meta.drift_range), fit_spec, '-', label='Current Spectrum')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig(meta.outputdir + 'figs/Fig44{}-CC_Spec.png'.format(str(n).zfill(int(np.floor(np.log10(meta.nspecchan))+1))))
    if not meta.hide_plots:
        plt.pause(0.2)

def cc_vals(meta, vals, n):
    '''Make the cross-correlation strength plot (Fig 4500).

    Parameters
    ----------
    meta:   MetaClass
        The metadata object.
    vals:   ndarray (1D)
        The cross-correlation strength.
    n:  int
        The current integration number.

    Returns
    -------
    None
    '''
    plt.figure(int('45{}'.format(str(0).zfill(int(np.floor(np.log10(meta.nspecchan))+1)))), figsize=(8, 8))
    plt.clf()
    plt.title(f'Cross Correlation - Values {n}')
    plt.plot(range(-meta.drift_range,meta.drift_range+1), vals, '.')
    plt.tight_layout()
    plt.savefig(meta.outputdir + 'figs/Fig45{}-CC_Vals.png'.format(str(n).zfill(int(np.floor(np.log10(meta.nspecchan))+1))))
    if not meta.hide_plots:
        plt.pause(0.2)
