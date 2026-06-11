# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)
import anywidget
import traitlets


class HoverButtonWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
      // Create container
      const container = document.createElement('div');
      container.style.position = 'relative';
      container.style.display = 'inline-block';
      container.style.height = '98%';

      // Create SVG container
      const svgContainer = document.createElement('div');
      svgContainer.style.width = '100%';
      svgContainer.style.lineHeight = '0';

      // Create log button
      const log_button = document.createElement('button');
      log_button.textContent = 'log';
      log_button.style.position = 'absolute';
      log_button.style.top = '5%';
      log_button.style.left = '20px';
      log_button.style.transform = 'translate(-50%, -50%)';
      log_button.style.padding = '4px 4px';
      log_button.style.fontSize = '1em';
      log_button.style.cursor = 'pointer';
      log_button.style.opacity = '0';
      log_button.style.backgroundColor = 'lightgray';
      log_button.style.color = 'black';
      log_button.style.border = '1px solid gray';
      log_button.style.borderRadius = '5px';

      // Create fit button
      const fit_button = document.createElement('button');
      fit_button.textContent = 'fit';
      fit_button.style.position = 'absolute';
      fit_button.style.bottom = '5%';
      fit_button.style.left = '20px';
      fit_button.style.transform = 'translate(-50%, 50%)';
      fit_button.style.padding = '4px 4px';
      fit_button.style.fontSize = '1em';
      fit_button.style.cursor = 'pointer';
      fit_button.style.opacity = '0';
      fit_button.style.backgroundColor = 'lightgray';
      fit_button.style.color = 'black';
      fit_button.style.border = '1px solid gray';
      fit_button.style.borderRadius = '5px';

      // Function to update SVG
      function updateSVG() {
        const svgData = model.get('svg_data');
        svgContainer.innerHTML = svgData;
        const svg = svgContainer.querySelector('svg');
        if (svg) {
          svg.style.width = '100%';
          svg.style.height = 'auto';
          svg.style.display = 'block';
        }
      }

      // Initial SVG
      updateSVG();

      // Show button on hover
      container.addEventListener('mouseenter', () => {
        log_button.style.opacity = '1';
        fit_button.style.opacity = '1';
      });

      container.addEventListener('mouseleave', () => {
        log_button.style.opacity = '0';
        fit_button.style.opacity = '0';
      });

      // Handle button click
      log_button.addEventListener('click', () => {
        model.send({ type: 'log_button_clicked' });
      });

      // Handle fit button click
      fit_button.addEventListener('click', () => {
        model.send({ type: 'fit_button_clicked' });
      });

      // Listen for SVG changes
      model.on('change:svg_data', updateSVG);

      // Listen for toggle state changes
      model.on('change:log_toggle_value', () => {
          const toggleValue = model.get('log_toggle_value');
          log_button.style.backgroundColor = toggleValue ? 'gray' : 'lightgray';
      });

      // Assemble widget
      container.appendChild(svgContainer);
      container.appendChild(log_button);
      container.appendChild(fit_button);
      el.appendChild(container);
    }
    export default { render };
    """

    # Traitlets
    svg_data = traitlets.Unicode('').tag(sync=True)
    log_toggle_value = traitlets.Bool(False).tag(sync=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_msg(self._handle_custom_msg)

    def _handle_custom_msg(self, content, buffers):
        """Handle messages from JavaScript"""
        if content.get('type') == 'log_button_clicked':
            if hasattr(self, '_log_button_click_handler'):
                self._log_button_click_handler()
        elif content.get('type') == 'fit_button_clicked':
            if hasattr(self, '_fit_button_click_handler'):
                self._fit_button_click_handler()

    def on_log_button_click(self, handler):
        """Register a callback function to be called when button is clicked"""
        self._log_button_click_handler = handler

    def on_fit_button_click(self, handler):
        """Register a callback function to be called when button is clicked"""
        self._fit_button_click_handler = handler

    def set_svg(self, svg_string):
        """Set SVG from a string"""
        self.svg_data = svg_string
