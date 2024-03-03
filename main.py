from chromatogram import ChromatogramRun

if __name__ == "__main__":
    run = ChromatogramRun('test_data.txt')

    # Find the peaks in the chromatogram
    peaks = run.find_peaks(
        normalize=True, # this will normalize the y values to be >= 0 preventing negative values for elution volume
        min_height=.15,
        distance=75,
        min_width=10,
        max_width=1000,
        relative_height=0.95
    )

    # Plot the chromatogram with peaks. Uncomment to see the plot
    # run.plot(peaks, show_widths=False, show_elution_volumes=True)

    # Plot each peak individually to verify the peak detection and integration
    # Uncomment to see the plots
    # for peak in peaks:
    #    peak.plot(run.x, run.y)

    print("Elusion volume (EU): ", run.total_elution_volume)
