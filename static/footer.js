class Footer extends React.Component {
  render() {
    return (
      e(
        "div", {
          className: "document-container footer-container"
        },
        this.props.acknowledgements ? e(
          "div", null,
          e(
            "div", {
              className: "footer-sub-title"
            },
            "Acknowledgements."
          ),
          e(
            "div", {
              className: "footer-content"
            },
            this.props.acknowledgements
          )
        ) : null,
        e(
          "div", {
            className: "footer-sub-title"
          },
          "License."
        ),
        e(
          "div", {
            className: "footer-content"
          },
          "All content is licensed under the Creative Commons Attribution ",
          e(
            "a", {
              href: "https://creativecommons.org/licenses/by/4.0/",
              target: "_blank"
            },
            "CC-BY 4.0"
          ),
          "."
        ),
        this.props.openSource ? e(
          "div", null,
          e(
            "div", {
              className: "footer-sub-title"
            },
            "Open-source."
          ),
          e(
            "div", {
              className: "footer-content"
            },
            this.props.openSource
          )
        ) : null,
        // e(
        //   "div", { className: "footer-sub-title" },
        //   "Donate."
        // ),
        // e(
        //   "div", { className: "footer-content" },
        //   "This project is born out of love for the ideas of the crypto community ❤️  We do not currently receive any funding and count on your support to allow us to continue.",
        //   e("br", null),
        //   e(
        //     "p", null,
        //     "Our address: ",
        //     e(
        //       "a", {
        //         href: "https://etherscan.io/address/hackingresearch.eth",
        //         target: "_blank"
        //       },
        //       "hackingresearch.eth"
        //     )
        //   )
        // ),
        e(
          "div", {
            id: "reference-container"
          }
        )
      )
    )
  }
}
