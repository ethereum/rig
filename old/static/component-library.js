const e = React.createElement;

class ExplorableInput extends React.Component {
  constructor(props) {
    super(props);
    this.handleMouseMove = this.handleMouseMove.bind(this);
    this.handleTouch = this.handleTouch.bind(this);

  }

  handleTouch(id,e) {
    if (e.type === 'touchstart') {
      this.props.updateStartX(e.touches[0].clientX);
    }

    if (e.type === 'touchmove') {
      this.props.updateCurrentX(e.touches[0].clientX,1,id);
    }

    if (e.type === 'touchend') {
      //see https://stackoverflow.com/questions/17957593/how-to-capture-touchend-coordinates (2nd answer)
      this.props.updateCurrentX(event.changedTouches[event.changedTouches.length-1].pageX,0,id);
    }

  }

  handleMouseMove(id,e) {
    e.preventDefault();

    if (e.type === 'mousedown') {
      this.props.updateStartX(e.clientX);

      // only listen for mousemove when mousedown
      onmousemove = (event) => {
        event.preventDefault();
        this.props.updateCurrentX(event.clientX,1,id);
      };

      onmouseup = (event) => {
        event.preventDefault();
        this.props.updateCurrentX(event.clientX,0,id);
        onmousemove = null;
        onmouseup = null;
      };
    }
  }

  render() {
    const value = this.props.value;
    const units = this.props.units ? this.props.units : '';
    const id = this.props.id;
    const format = d3.format(',');

    return (
      e(
        'button', {
          className: 'adjustable',
          onMouseDown: (e) => this.handleMouseMove(id,e),
          onTouchStart: (e) => this.handleTouch(id,e),
          onTouchMove: (e) => this.handleTouch(id,e),
          onTouchEnd: (e) => this.handleTouch(id,e)
        },
        format(value) + " " + units
      )
    );
  }
}

class ExplorableOutput extends React.Component {
  render() {
    const calcDisplay = this.props.calcDisplay;
    const value = this.props.value;
    return (
      e(
        'span', {
          className: 'output',
          style: {
            fontWeight: 400,
            background: calcDisplay ? 'rgba(3,136,166,1.0)' : 'none',
            color: calcDisplay ? 'white' : 'rgba(3,136,166,1.0)',
            cursor: 'pointer'
          },
          onClick: this.props.onClick
        },
        value
      )
    );
  }
}

class CalculationLine extends React.Component {
  render() {
    const left = this.props.left;
    var right = this.props.right;
    var rightClass = 'calculations-line-right';
    const format = (x) => d3.format(',')(d3.format('.2f')(x));

    if (typeof right === 'number') { right = format(right) }

    return (
      e(
        'div', { className: 'calculations-line' },
        e(
          'div', { className: 'calculations-line-left' },
          left
        ),
        e(
          'div', { className: 'calculations-line-operator'},
          "="
        ),
        e(
          'div', { className: rightClass },
          right
        )
      )
    );
  }
}

class CalculationLine2 extends React.Component {
  render() {
    const left = this.props.left; //::string
    const right = this.props.right; //::array
    const shift = this.props.shift ? true : false;
    var working = [];

    right.map(function(d,i) {
      if ((!shift && (i % 2 === 0)) || (shift && (i % 2 === 1))) { // we are dealing with a word
        working.push(
          e(
            'span', { className: 'calculations-line-bubble' },
            d
          )
        );
      }

      if ((!shift && (i % 2 === 1)) || (shift && (i % 2 === 0))) { // we are dealing with a symbol
        working.push(
          e(
            'span', { className: 'calculations-line-symbol' },
            d
          )
        );
      }
    });

    return (
      e(
        'span', { className: 'calculations-line' },
        e(
          'span', { className: 'calculations-line-left' },
          left
        ),
        e(
          'span', { className: 'calculations-line-right' },
          " = "
        ),
        e(
          'span', { className: 'calculations-line-right' },
          working
        )
      )
    );
  }
}

class CalculationComment extends React.Component {
  render() {
    const comment = this.props.comment;

    return e(
      'div', { className: 'calculations-comment' },
      comment
    );
  }
}

class CalculationSpace extends React.Component {
  render() {
    return e('div', { className: 'calculations-space' });
  }
}

class CalculationWrapper extends React.Component {
  render() {
    return (
      e(
        'div', {
          className: 'calculations-container',
          style: {
            paddingTop: '0.5rem'
          }
        },
        e(
          'div', { className: 'calculations-title-container' },
          e(
            'span', { className: 'calculations-title'},
            this.props.title
          ),
          e(
            'span', { className: 'calculation-title-comment' },
            this.props.comment ? (' ' + this.props.comment) : ''
          )
        ),
        e(
          'div', { className: 'calculation-analysis' },
          // e(CalculationSpace, null),
          this.props.children
        )
      )
    );
  }
}

// D3 stuff
class D3Component extends React.Component {
  constructor(props) {
    super(props);
    this.createVisual = this.createVisual.bind(this);
    this.updateVisual = this.updateVisual.bind(this);
    this.render = this.render.bind(this);
    this.elementId = props.elementId;
    this.state = {
      width: 0
    };
  }

  updateDimensions() {
    const width = this.element ? this.element.clientWidth : this.state.width;
    this.setState({ width });
  }

  componentDidMount() {
    const width = this.element.clientWidth;
    this.setState({
      width: width
    }, () => {
      this.createVisual();
      this.updateVisual();
      window.addEventListener("resize", this.updateDimensions.bind(this));
    });
  }

  componentDidUpdate() {
//    console.log("did update");
    this.updateVisual();
  }

  componentWillUnmount() {
    d3.select(window).on("resize", null);
  }

  createVisual() { }

  updateVisual() { }

  render() {
    return (
      e(
         "div", {
          ref: (element => this.element = element),
          style: {
            height: this.props.height + "px"
          }
        },
        e(
          "svg", {
            ref: (node => this.node = node),
            width: this.state.width,
            height: this.props.height
          }
        )
      )
    );
  }
}

// Data visualisations
class ExplorableSeries extends D3Component {
  createVisual() {
    var that = this;

    var margin = { top: 10, right: 20, bottom: 45, left: 70 },
    width = this.state.width - margin.left - margin.right,
    height = this.props.height - margin.top - margin.bottom;

    const node = this.node;
    const svg = d3.select(node)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .attr("id", "svg-" + this.props.elementId);

    svg.append("g")
    .attr("class", "x axis");
    svg.append("g")
    .attr("class", "y axis");
    svg.append("g")
    .attr("id", "svg-" + this.props.elementId + "-x-axis-label");
    svg.append("g")
    .attr("id", "svg-" + this.props.elementId + "-y-axis-label");
  }

  updateVisual() {
    const that = this;
    const svg = d3.select("#svg-" + this.props.elementId);

    var margin = { top: 10, right: 20, bottom: 45, left: 70 },
    width = this.state.width - margin.left - margin.right,
    height = this.props.height - margin.top - margin.bottom;

    var x = d3.scaleLinear().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);

    x.domain([0, d3.max(that.props.dataPoints)]);
    y.domain([
      0,
      d3.max(
        that.props.series,
        serie => d3.max(that.props.dataPoints, d => serie.getData(d))
      )
    ]);

    const xmin = d3.min(that.props.dataPoints);
    const xmax = d3.max(that.props.dataPoints);
    const tickNumber = that.props.xAxis.tickNumber ? that.props.xAxis.tickNumber : 5;
    const tickValues = that.props.tickValues ? that.props.tickValues : d3.range(xmin, xmax, (xmax - xmin) / tickNumber).concat(xmax);

    svg.select(".x.axis")
      .attr("transform", "translate(0," + height + ")")
      .call(
        d3.axisBottom(x).tickValues(
          that.props.xAxis.hideTicks ? [] : tickValues
        ).tickFormat(that.props.xAxis.format)
      );

    svg.select(".y.axis")
      .call(
        d3.axisLeft(y).ticks(that.props.yAxis.hideTicks ? 0 : 3).tickFormat(this.props.yAxis.format)
      );

    const lineStart = function(d, i) {
      const leftMargin = 0;
      return leftMargin + i * ((width - leftMargin) / that.props.series.length);
    }

    const lineSize = function(d) {
      return (d.size ? d.size : 0.5) + "px";
    }

    const xLabelMargin = 35;
    const xLegendMargin = xLabelMargin + 20;

    const xAxisLabelSVG = svg.select("#svg-" + this.props.elementId + "-x-axis-label")
    .selectAll(".axis-label")
    .data([this.props.xAxis.label]);
    xAxisLabelSVG.enter()
    .append("text")
    .attr("class", "axis-label")
    .attr("dominant-baseline", "middle")
    .text(d => d)
    .attr("transform", "translate(" + 0 + ","+ (height + xLabelMargin) +")");
    xAxisLabelSVG
    .attr("transform", "translate(" + 0 + ","+ (height + xLabelMargin) +")");

    const yAxisLabelSVG = svg.select("#svg-" + this.props.elementId + "-y-axis-label")
    .selectAll(".axis-label")
    .data([this.props.yAxis.label]);
    yAxisLabelSVG.enter()
    .append("text")
    .attr("class", "axis-label")
    .text(d => d)
    .attr("transform", "translate(-" + (margin.left-20) +","+height+")rotate(-90)");
    yAxisLabelSVG
    .attr("transform", "translate(-" + (margin.left-20) +","+height+")rotate(-90)");

    var closeToXEnd = function(d) {
      return (0.8 * width - x(d) < 0);
    }

    var closeToYStart = function(d) {
      return (0.2 * height - y(that.props.series[0].getData(d)) > 0);
    }

    var data = this.props.series.map(
      series => _.extend(series, {
        points: this.props.dataPoints.map(
          d => {
            return {
              x: d,
              y: series.getData(d)
            }
          }
        )
      })
    );

    var valueline = d3.line()
    .x(d => x(d.x))
    .y(d => y(d.y));

    var linePath = svg.selectAll(".series-line")
    .data(data);
    linePath.attr("d", d => valueline(d.points));
    linePath.enter()
    .append("path")
    .attr("class", "series-line")
    .attr("d", d => valueline(d.points))
    .style("stroke", d => d.colour)
    .style("fill", "none")
    .style("stroke-width", lineSize);

    if (this.props.currentPoint) {
      const followPointsData = this.props.series.map(
        series => {
          return {
            x: this.props.currentPoint,
            y: series.getData(this.props.currentPoint),
            colour: series.colour
          };
        }
      );

      var followLineHor = svg.selectAll(".follow-line-hor")
      .data(followPointsData);
      followLineHor.exit()
      .remove();
      followLineHor.attr("x2", d => x(d.x))
      .attr("y1", d => y(d.y))
      .attr("y2", d => y(d.y));
      followLineHor.enter()
      .append("line")
      .attr("x1", d => x(0))
      .attr("x2", d => x(d.x))
      .attr("y1", d => y(d.y))
      .attr("y2", d => y(d.y))
      .attr("class", "chart-follow follow-line follow-line-hor")
      .attr("stroke-dasharray", "5, 5")
      .style("stroke", d => d.colour);

      var followPoint = svg.selectAll(".follow-point")
      .data(followPointsData);
      followPoint.exit()
      .remove();
      followPoint
      .attr("cx", d => x(d.x))
      .attr("cy", d => y(d.y));
      followPoint.enter()
      .append("circle")
      .attr("cx", d => x(d.x))
      .attr("cy", d => y(d.y))
      .attr("r", 4)
      .attr("class", "chart-follow follow-point")
      .style("fill", d => d.colour);
    }
  }
}

class PlotLegendVisual extends D3Component {
  createVisual() {
    const node = this.node;
    this.svg = d3.select(node)
    .append("g")
    .attr("id", "svg-" + this.props.elementId);
  }

  updateVisual() {
    if (!this.svg) {
      return;
    }
    if (this.props.visualType == "line") {
      const lineSize = (this.props.lineSize ? this.props.lineSize : "0.5") + "px";
      const legendLineSVG = this.svg.selectAll(".legend-line")
      .data([{}]);

      legendLineSVG.enter()
      .append("line")
      .attr("x1", 0)
      .attr("x2", this.state.width)
      .attr("y1", 2 * this.props.height / 3)
      .attr("y2", 2 * this.props.height / 3)
      .style("stroke", this.props.colour)
      .style("stroke-width", lineSize)
      .attr("class", "legend-line");
    }
  }
}

class PlotLegendText extends React.Component {
  render() {
    return (
      e(
        "div", {
          className: "legend-text"
        },
        this.props.legendText
      )
    )
  }
}

class PlotLegend extends React.Component {
  render() {
//    console.log(this.props.items);
    return (
      e(
        "div", {
          className: "legend-container",
          style: {
            marginLeft: this.props.marginLeft
          }
        },
        this.props.items.map(
          item => e(
            "div", {
              className: "legend-item-container"
            },
            e(
              "div", {
                className: "legend-visual"
              },
              e(
                PlotLegendVisual, {
                  height: 20,
                  lineSize: item.lineSize,
                  visualType: this.props.visualType,
                  colour: item.colour
                }
              )
            ),
            e(
              PlotLegendText, {
                legendText: item.name
              }
            )
          )
        )
      )
    );
  }
}

class ExplorableWithLegend extends React.Component {
  render() {
    return (
      e(
        "div", null,
        this.props.children,
        e(
          PlotLegend, {
            visualType: "line",
            items: this.props.series,
            marginLeft: "70px"
          }
        )
      )
    )
  }
}

// Figures
class FigureCaption extends React.Component {
  render() {
    return (
      e(
        "div", { className: "figure-caption-container" },
        e(
          "div", { className: "figure-title-container" },
          e(
            "span", {
              className: "figure-title " + this.props.type.toLowerCase() + "-title"
            },
            this.props.type,
            e(
              "span", {
                className: "figure-number " + this.props.type.toLowerCase() + "-number"
              }
            ),
            ". "
          ),
          e(
            "span", { className: "figure-name" }, this.props.name
          )
        ),
        e(
          "div", { className: "figure-caption" },
          this.props.caption ? this.props.caption : e("div", null),
          this.props.children
        )
      )
    );
  }
}

class StaticLink extends React.Component {
  render() {
    return (
      e(
        'div', { className: 'static-link-container' },
        e(
          'a', {
            href: this.props.href,
            target: '_blank'
          },
          e(
            FigureCaption, {
              type: "Link",
              name: this.props.name,
              caption: this.props.caption
            },
            this.props.children
          )
        )
      )
    );
  }
}

class Definition extends React.Component {
  render() {
    return (
      e(
        'div', { className: 'definition-container' },
        e(
          FigureCaption, {
            type: "Definition",
            name: this.props.name,
            caption: this.props.caption
          },
          this.props.children
        )
      )
    );
  }
}

class InteractiveFigure extends React.Component {
  render() {
    return (
      e(
        'div', { className: 'static-image-container' },
        e(
          FigureCaption, {
            type: "Image",
            name: this.props.name,
            caption: this.props.caption
          }
        ),
        e(
          "div", null,
          this.props.children
        )
      )
    )
  }
}

class StaticImage extends React.Component {
  render() {
    return (
      e(
        'div', { className: 'static-image-container' },
        e(
          FigureCaption, {
            type: "Image",
            name: this.props.name,
            caption: this.props.caption
          },
          this.props.children
        ),
        e(
          'img', {
            src: this.props.src,
            alt: this.props.name
          }
        )
      )
    )
  }
}

class Table extends React.Component {
  render() {
    return (
      e(
        'div', { className: 'static-table-container' },
        e(
          "table", { className: this.props.tableClass },
          e(
            "thead", null,
            e(
              "tr", null,
              Object.keys(_.omit(this.props.data[0], "hidden")).map(
                key => e(
                  "th", null,
                  key
                )
              )
            )
          ),
          e(
            "tbody", null,
            this.props.data.map(
              d => e(
                "tr", {
                  style: {
                    color: d.hidden.highlight ? "rgba(3,136,166,1.0)" : "rgb(56,56,56,0.8)"
                  }
                },
                Object.keys(_.omit(d, "hidden")).map(
                  key => e(
                    "td", null,
                    d[key]
                  )
                )
              )
            )
          )
        ),
        e(
          FigureCaption, {
            type: "Table",
            name: this.props.name,
            caption: this.props.caption
          },
          this.props.children
        )
      )
    );
  }
}

// References
class ReferenceInText extends React.Component {
  render() {
    return (
      e(
        'a', { href: "#reference-container" },
        ' [',
        this.props.refidx.join(", "),
        ']'
      )
    );
  }
}

class ReferenceItem extends React.Component {
  render() {
    return (
      e(
        'div', { className: 'reference-item-container' },
        e(
          'div', { className: "reference-item-number" },
          e(
            'a', { href: this.props.href },
            '[',
            this.props.refidx,
            '] '
          )
        ),
        this.props.children
      )
    );
  }
}

class ReferenceFootnote extends React.Component {
  render() {
    return (
      e(
        ReferenceItem, {
          refidx: this.props.refidx,
          href: "#ref-" + this.props.href
        },
        this.props.content
      )
    );
  }
}

class ReferenceBibliography extends React.Component {
  render() {
    var link = "";
    if (this.props.url) {
      link = e(
        "span", null,
        " ",
        e(
          "a", {
            href: this.props.url,
            target: "_blank"
          },
          "[Link]"
        )
      );
    }
    return (
      e(
        ReferenceItem, {
          refidx: this.props.refidx,
          href: "#ref-" + this.props.href
        },
        e(
          "div", { className: "reference-item" },
          e(
            "div", { className: "reference-title" },
            this.props.title
          ),
          e(
            "div", { className: "reference-details" },
            this.props.author,
            ', ',
            this.props.year,
            link,
            '.'
          )
        )
      )
    );
  }
}

class ReferenceContainer extends React.Component {
  render() {
    return (
      e(
        'div', { className: 'reference-container' },
        e(
          'div', { className: 'footer-sub-title' },
          'References.'
        ),
        this.props.references.map(
          (bib, refidx) => {
            if (bib.content) {
              return e(
                ReferenceFootnote,
                _.extend(bib, {
                  refidx: refidx + 1,
                  key: refidx + 1
                })
              );
            } else {
              return e(
                ReferenceBibliography,
                _.extend(bib, {
                  refidx: refidx + 1,
                  key: refidx + 1
                })
              );
            }
          }
        )
      )
    )
  }
}

// Bimatrices
class BimatrixCell extends React.Component {
  render() {
    return e(
      "td",
      { className: "bimatrix-payoff-cell" },
      e(
        "span",
        { className: "bimatrix-payoff bimatrix-payoff-p1" },
        this.props.payoff1
      ),
      this.props.payoff2 ? ", " : null,
      this.props.payoff2 ? e(
        "span",
        { className: "bimatrix-payoff bimatrix-payoff-p2" },
        this.props.payoff2
      ) : null
    );
  }
}

class BimatrixStrategyCell extends React.Component {
  render() {
    return e(
      "td",
      { className: "bimatrix-strategy-cell bimatrix-strategy-" + this.props.player },
      this.props.strategy
    );
  }
}

class BimatrixHeaderRow extends React.Component {
  render() {
    return e(
      "tr",
      null,
      e(
        "td",
        null
      ),
      this.props.strategies.map(
        strategy => e(
          BimatrixStrategyCell, {
            strategy: strategy,
            player: "p2",
            key: strategy
          }
        )
      )
    );
  }
}

class BimatrixRow extends React.Component {
  render() {
    return e(
      "tr",
      null,
      e(
        BimatrixStrategyCell,
        { strategy: this.props.strategy, player: "p1" }
      ),
      this.props.payoffs.map(
        (payoffs, idx) => e(
          BimatrixCell, {
            payoff1: payoffs[0],
            payoff2: payoffs[1],
            key: idx
          }
        )
      )
    );
  }
}

class BimatrixHelpButton extends React.Component {
  render() {
    return (
      e(
        'div', null,
        e(
          'p', {
            className: 'help-button',
            onClick: this.props.onClick
          },
          "How do I read this table?"
        )
      )
    );
  }
}

class BimatrixHelpExplanation extends React.Component {
  render() {
    return (
      e(
        'div', {
          className: 'bimatrix-help-explanation-container',
          style: {
            display: this.props.showHelp ? 'block' : 'none'
          }
        },
        this.props.payoffs[this.props.strategy1][this.props.strategy2].length == 1 ?
        e(
          "span", null,
          'This table shows the rewards for Bob under different actions. For example, if ',
          this.props.strategies.player1[this.props.strategy1],
          ' and ',
          this.props.strategies.player2[this.props.strategy2],
          ', Bob receives a reward  ',
          e(
            'span', { className: 'bimatrix-payoff-p1' }, this.props.payoffs[this.props.strategy1][this.props.strategy2][0]
          ),
          '.'
        ) :
        e(
          "span", null,
          'This table shows the payoffs of two players, ',
          e(
            "span", { className: 'bimatrix-strategy-p1' },
            this.props.name1 ? this.props.name1 : "Row"
          ),
          " and ",
          e(
            "span", { className: 'bimatrix-strategy-p2' },
            this.props.name2 ? this.props.name2 : "Column"
          ),
          '. For instance, if ',
          e(
            "span", { className: 'bimatrix-strategy-p1' }, this.props.strategies.player1[this.props.strategy1]
          ),
          " and ",
          e(
            'span', { className: 'bimatrix-strategy-p2' }, this.props.strategies.player2[this.props.strategy2]
          ),
          ", then ",
          e(
            "span", { className: 'bimatrix-strategy-p1' },
            this.props.name1 ? this.props.name1 : "Row"
          ),
          " receives a payoff of ",
          e(
            'span', { className: 'bimatrix-payoff-p1' }, this.props.payoffs[this.props.strategy1][this.props.strategy2][0]
          ),
          " and ",
          e(
            "span", { className: 'bimatrix-strategy-p2' },
            this.props.name2 ? this.props.name2 : "Column"
          ),
          " receives a payoff of ",
          e(
            'span', { className: 'bimatrix-payoff-p2' }, this.props.payoffs[this.props.strategy1][this.props.strategy2][1]
          ),
          "."
        )
      )
    );
  }
}

class BimatrixHelp extends React.Component {
  render() {
    return (
      e(
        'div', { className: 'bimatrix-help-container' },
        e(
          BimatrixHelpButton, {
            showHelp: this.props.showHelp,
            onClick: this.props.onClick
          }
        ),
        e(
          BimatrixHelpExplanation, {
            showHelp: this.props.showHelp,
            strategies: this.props.strategies,
            strategy1: this.props.strategy1,
            strategy2: this.props.strategy2,
            name1: this.props.name1,
            name2: this.props.name2,
            payoffs: this.props.payoffs
          }
        )
      )
    );
  }
}

class BimatrixGame extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showHelp: false
    }
    this.onClick = this.onClick.bind(this)
  }

  onClick(e) {
    this.setState({
      showHelp: !this.state.showHelp
    });
  }

  render() {
    return (
      e(
        "div",
        { className: "bimatrix-container" },
        e(
          FigureCaption, {
            type: "Table",
            name: this.props.name,
            caption: this.props.caption
          }
        ),
        e(
          "table",
          { className: "bimatrix" },
          e(
            "thead", null,
            e(
              BimatrixHeaderRow, {
                strategies: this.props.strategies.player2
              }
            )
          ),
          e(
            "tbody", null,
            this.props.payoffs.map(
              (payoffs, idx) => e(
                BimatrixRow, {
                  payoffs: payoffs,
                  strategy: this.props.strategies.player1[idx],
                  key: idx
                }
              )
            )
          )
        ),
        e(
          BimatrixHelp, {
            showHelp: this.state.showHelp,
            onClick: this.onClick,
            strategies: this.props.strategies,
            strategy1: this.props.helpStrategy1,
            strategy2: this.props.helpStrategy2,
            name1: this.props.name1,
            name2: this.props.name2,
            payoffs: this.props.payoffs
          }
        )
      )
    );
  }
}

class ExplorableComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      startX: 0,
      currentX: 0
    };
    this.inputs = {};

    this.updateStartX = this.updateStartX.bind(this);
    this.updateCurrentX = this.updateCurrentX.bind(this);
    this.registerInputs = this.registerInputs.bind(this);
  }

  registerInputs() {
    const that = this;
    Object.keys(this.inputs).forEach(
      input => {
        that.state["start"+input] = that.inputs[input].start;
        that.state[input] = that.inputs[input].start;
      }
    );
  }

  updateStartX(startX) {
    this.setState({
      startX: startX
    });
  }

  updateCurrentX(currentX, mousemove, id) {
    var range;
    var lowerb;
    var upperb;
    var sensitivity;
    var startValue = 'start' + id;
    var that = this;
    var format;

    if (this.inputs[id]) {
      const input = this.inputs[id];
      range = input.range;
      lowerb = input.lowerb;
      upperb = input.upperb;
      sensitivity = input.sensitivity;
      format = input.format;
    }

    var x = d3.scaleLinear()
    .domain([-sensitivity,sensitivity])
    .range([that.state[startValue] - range, that.state[startValue] + range])
    .clamp(true);

    var newValue = x(currentX - that.state.startX);
    if (newValue < lowerb) { newValue = lowerb; }
    if (newValue > upperb) { newValue = upperb; }

    newValue = format(newValue);

    this.setState({
      currentX: currentX,
      [id]: +newValue,
      [startValue]: mousemove === 1 ? this.state[startValue] : +newValue
    });
  }
}

class ContentListItem extends React.Component {
  render() {
    return (
      e(
        'div', { className: 'content-list-item' },
        e(
          'a', { href: this.props.content.href },
          e(
            'div', { className: 'content-list-item-title' },
            this.props.content.title
          ),
          e(
            'div', { className: 'content-list-item-date' },
            this.props.content.date
          ),
          e(
            'div', { className: 'content-list-item-abstract' },
            this.props.content.abstract
          )
        )
      )
    );
  }
}

class ContentList extends React.Component {
  render() {
    return (
      e(
        "div", { className: 'content-list-container' },
        this.props.content.map(
          content => e(
            ContentListItem, { content }
          )
        )
      )
    );
  }
}

class RadioButtons extends React.Component {
  render() {
    return (
      e(
        "div", { id: this.props.elementId },
        e(
          "div", { className: "radio-title" },
          this.props.name
        ),
        e(
          "div", {
            className: "radio-buttons-container",
            style: { display: "flex" }
          },
          this.props.values.map(
            (value, i) => e(
              "button", {
                style: {
                  border: (this.props.selectedButton == i ? "2px" : "0.5px") + " solid " + this.props.fillColors[i],
                  width: this.props.buttonWidth,
                  height: this.props.buttonHeight,
                  color: "rgb(56, 56, 56)",
                  textDecoration: "none"
                },
                onClick: d => this.props.onClick(i),
                key: i
              },
              value
            )
          )
        )
      )
    );
  }
}

class TOCSection extends React.Component {
  render() {
    return (
      e(
        "div", { className: "toc-section" },
        e(
          "div", { className: "toc-section-title" },
          e(
            "a", { href: "#sec-" + this.props.secidx },
            e(
              "span", { className: "toc-section-number" },
              this.props.secidx + ". "
            ),
            this.props.section.section.name
          )
        ),
        this.props.section.subsections.map(
          (subsection, subsecidx) => e(
            TOCSubSection, {
              subsection: subsection,
              secidx: this.props.secidx,
              subsecidx: subsecidx + 1,
              key: this.props.secidx + "-" + (subsecidx + 1)
            }
          )
        )
      )
    );
  }
}

class TOCSubSection extends React.Component {
  render() {
    return (
      e(
        "div", { className: "toc-sub-section" },
        e(
          "div", { className: "toc-sub-section-title" },
          e(
            "a", { href: "#subsec-" + this.props.secidx + "-" + this.props.subsecidx },
            e(
              "span", {
                className: "toc-sub-section-number"
              },
              this.props.secidx + "." + this.props.subsecidx + " "
            ),
            this.props.subsection.name
          )
        )
      )
    );
  }
}

class TOC extends React.Component {
  render() {
    return (
      e(
        "div", { className: "toc-container" },
        e(
          "div", { className: "toc-container-title" },
          "Table of contents"
        ),
        e(
          "div", { className: "toc-sections-container" },
          this.props.sections.map(
            (section, secidx) => e(
              TOCSection, {
                section: section,
                secidx: secidx + 1,
                key: section+"-"+(secidx+1)
              }
            )
          )
        )
      )
    );
  }
}

class AuthorComponent extends React.Component {
  render() {
    return (
      e(
        "div", { key: this.props.name },
        e(
          "div", { className: "author-block-author" },
          e(
            "a", { href: this.props.link, target: "_blank" },
            this.props.name
          )
        ),
        e(
          "div", { className: "author-block-affiliation" },
          this.props.affiliation
        )
      )
    );
  }
}

class AuthorSacha extends React.Component {
  render() {
    return (
      e(
        AuthorComponent, {
          name: "Sacha Yves Saint-Léger",
          affiliation: "hackingresear.ch",
          link: "https://twitter.com/yslcrypto"
        }
      )
    )
  }
}

class AuthorBarnabe extends React.Component {
  render() {
    return (
      e(
        AuthorComponent, {
          name: "Barnabé Monnot",
          affiliation: "Ethereum Foundation, Robust Incentives Group",
          link: "https://twitter.com/barnabemonnot"
        }
      )
    )
  }
}

class AuthorCaspar extends React.Component {
  render() {
    return (
      e(
        AuthorComponent, {
          name: "Caspar Schwarz-Schilling",
          affiliation: "Ethereum Foundation, Robust Incentives Group",
          link: "https://twitter.com/casparschwa"
        }
      )
    )
  }
}

class AuthorShyam extends React.Component {
  render() {
    return (
      e(
        AuthorComponent, {
          name: "Shyam Sridhar",
          affiliation: "Ethereum Foundation, Robust Incentives Group",
          link: "https://github.com/shsr2001"
        }
      )
    )
  }
}

class AuthorFred extends React.Component {
  render() {
    return (
      e(
        AuthorComponent, {
          name: "0x66726564",
          affiliation: "",
          link: "https://twitter.com/0x66726564"
        }
      )
    )
  }
}

class AuthorAditya extends React.Component {
  render() {
    return (
      e(
        AuthorComponent, {
          name: "Aditya Asgaonkar",
          affiliation: "Ethereum Foundation",
          link: "https://twitter.com/adiasg"
        }
      )
    )
  }
}

class AuthorBlock extends React.Component {
  render() {
    return (
      e(
        "div", {
          className: "author-block-container"
        },
        e(
          "div", { className: "author-block-title" },
          "Authors"
        ),
        e(
          "div", null,
          e(
            "div", {
              className: "author-block-authors"
            },
            this.props.authors.map(
              author => {
                if (author == "sacha") return e(AuthorSacha)
                else if (author == "barnabe") return e(AuthorBarnabe)
                else if (author == "shyam") return e(AuthorShyam)
                else if (author == "caspar") return e(AuthorCaspar)
                else if (author == "aditya") return e(AuthorAditya)
                else if (author == "fred") return e(AuthorFred)
                else return e(AuthorComponent, { author: author })
              }
            )
          )
        )
      )
    );
  }
}

class FixedWidthList extends React.Component {
  render() {
    return (
      e(
        "div", { className: "fixed-width-list-container" },
        this.props.data.map(
          (d, i) => e(
            "div", {
              className: "fixed-width-list-item" +
              (d.highlighted ? " fixed-width-list-item-highlighted" : "")
            },
            e(
              "a", {
                href: d.href,
                target: "_blank"
              },
              e(
                "span", {
                  className: "fixed-width-list-number"
                },
                i + 1
              ),
              d.title
            )
          )
        )
      )
    )
  }
}

class Box extends React.Component {
  render() {
    return (
      e(
        "div", {
          className: "box-container"
        },
        e(
          "div", {
            className: "box-title-container",
          },
          e(
            "div", { className: "box-title" },
            this.props.title
          )
        ),
        this.props.children,
        e(
          "div", {
            className: "box-close"
          }
        )
      )
    );
  }
}

class ExpandableComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      expanded: this.props.expanded ? this.props.expanded : false
    }
  }

  componentDidUpdate() {
    if (this.ref2) {
      let math = this.ref2.getElementsByClassName('math');
      for (var i = 0; i < math.length; i++) {
        katex.render(math[i].innerText, math[i]);
      }
    }
  }

  render() {
    return (
      e(
        "div", {
          className: "related-idea-container"
        },
        e(
          "div", {
            className: "related-idea",
            ref: (ref => this.ref = ref),
            onClick: (e) => {
              this.setState({ expanded: !this.state.expanded });
            }
          },
          e("span", { className: "related-idea-caret" }, "Expand "),
          e(
            "div", { className: "related-idea-title" },
            this.props.title
          ),
          e(
            "div", { className: "expand-button" },
            this.state.expanded ? "Close x" : "Expand +"
          )
        ),
        !this.state.expanded ? e(
          "div", { className: "related-idea-description" },
          this.props.description
        ) : null,
        (this.state.expanded ? e(
          "div", {
            ref: (ref => this.ref2 = ref)
          },
          this.props.children,
          e(
            "div", {
              className: "related-idea related-idea-close",
              onClick: (e) => {
                if (this.state.expanded) {
                  this.ref.scrollIntoView({ behavior: 'smooth' });
                }
                this.setState({ expanded: !this.state.expanded });
              }
            },
            // e("span", { className: "related-idea-caret" }, "> "),
            // "Close",
            // " \"" + this.props.title + "\"",
            e(
              "div", { className: "related-idea-title" },
              ""
            ),
            e(
              "div", { className: "expand-button" },
              this.state.expanded ? "Close x" : "+"
            )
          )
        ) : null),
      )
    );
  }
}
