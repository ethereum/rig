let refs = document.getElementsByClassName('reference');
Object.values(refs).forEach(
  (ref, idx) => {
    if (Object.values(refs).map(
      r => r.getAttribute('refid')
    ).indexOf(ref.getAttribute('refid')) == idx) {
      ref.setAttribute('id', 'ref-' + ref.getAttribute('refid').split(" ")[0]);
    }
  }
);
let bibliographyData = _.uniq(
  Object.values(refs).reduce(
    (acc, ref) => {
      let refids = ref.getAttribute('refid').split(" ");
      return acc.concat(
        refids.map(
          refid => {
            let extendedRef = _.extend(
              referenceData[refid], { refid: refid, href: refids[0] }
            );
            return extendedRef;
          }
        )
      );
    }, []
  ),
  item => {
    return item.refid;
  }
);

Object.values(refs).forEach(
  d => {
    let refidx = d.getAttribute('refid').split(" ")
    .map(
      ref => _.indexOf(
        bibliographyData.map(bib => bib.refid),
        ref
      ) + 1
    );
    ReactDOM.render(
      React.createElement(ReferenceInText, { refidx }),
      d
    );
  }
);

ReactDOM.render(
  React.createElement(ReferenceContainer, {
    references: bibliographyData
  }),
  document.querySelector("#reference-container")
);
