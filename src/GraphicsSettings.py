class TimeDomainParameters:
    time_amplitude = 40
    do_time_domain_plot = False


class FrequencyDomainParameters:
    min_db_power = -45
    max_db_power = 10
    outside_db_to_plot = 10
    max_plot_frequency = 40
    do_frequency_domain_plot = False
    do_frequency_domain_as_colored_scatter = True


class RenderSettings:
    figure_size = [10, 10]
    font_size = 18
    tick_size = 14
    dpi = 100
    do_render_plot_axis = True
    fps = 40

class ProcessingSettings:
    T_slow = 20*60
    T_fast = 2.5
    channel_number = 0

class GraphicsSettings:
    timeDomainParameters = TimeDomainParameters()
    frequencyDomainParameters = FrequencyDomainParameters()
    renderSettings = RenderSettings()
