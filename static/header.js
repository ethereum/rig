class Header extends React.Component {
  render() {
    const e = React.createElement;

    return (
      e(
        'div', {	className: 'rig-header' },
        e(
          "div", { className: "header-container" },
          e('a', { href: 'https://github.com/ethereum/rig', className: 'nav-logo' }, "Robust Incentives Group"),
          e(
            'ul', { className: "nav-menu" },
            e('li', { className: 'nav-item' }, e('a', { href: 'https://ethereum.github.io/abm1559' }, "eip1559")),
            e('li', { className: 'nav-item' }, e('a', { href: 'https://ethereum.github.io/beaconrunner' }, "PoS")),
            e('li', { className: 'nav-item' }, e('a', { href: 'https://shsr2001.github.io/beacondigest' }, "beacondigest")),
          ),
          e(
            'div', { className: "hamburger" }, "🍔"
          )
            // e(
            //   'div', { className: "header-right-element" },
            //   e('a', { href: '/abm1559' }, "eip1559")
            // ),
            // e(
            //   'div', { className: "header-right-element" },
            //   e('a', { href: '/beaconrunner' }, "eth2")
            // )
            // e(
            //   'div', { className: "header-right-element" },
            //   e('a', { href: '/about' }, 'About')
            // ),
            // e(
            //   'div', { className: "header-right-element" },
            //   e('a', { href: 'https://twitter.com/hackingresearch' }, 'Twitter')
            // )
        )
      )
    );
  }
}
