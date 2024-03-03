from chromatogram import ChromatogramRun

if __name__ == "__main__":
    run = ChromatogramRun('test_data.txt')

    # The peaks are already found and stored using the default peak-finding parameters
    run.peaks

    # To find peaks using custom parameters:
    run.find_peaks(
        normalize=True,
        distance=75,
        min_width=10,
        max_width=1000,
        relative_height=0.95
    )

    # Print each peak including elution volumes.
    [print(peak) for peak in run.peaks]

    # Plot the chromatogram with peaks.
    run.plot(show_widths=True, show_elution_volumes=True)

    # Plot each peak individually to verify the peak detection and integration
    # Uncomment to see the plots
    # for peak in run.peaks:
    #    peak.plot(run.times, run.values)
