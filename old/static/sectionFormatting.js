const formatSection = function(section) {
  return {
    name: section.text
  }
};

Object.values(document.getElementsByTagName('h2')).forEach((item, i) => {
  item.setAttribute('class', 'section-title section-label')
});

Object.values(document.getElementsByTagName('h3')).forEach((item, i) => {
  item.setAttribute('class', 'section-sub-title section-label')
});

const titles = document.getElementsByClassName('section-label');
const unformattedSections = Object.values(titles).map(
  (title, idx) => [title, idx]
).filter(
  d => d[0].getAttribute('class').includes('section-title')
).map(
  (d, i, a) => {
    return {
      section: {
        element: d[0],
        secidx: i+1,
        id: d[0].getAttribute('id'),
        text: d[0].innerText
      },
      subsections: Object.values(titles).filter(
        (title, idx) => title.getAttribute('class').includes('section-sub-title') && (idx < (i == (a.length-1) ? titles.length : a[i+1][1])) && (idx > a[i][1])
      ).map(
        (el, idx) => {
          return {
            element: el,
            secidx: i+1,
            subidx: idx+1,
            id: el.getAttribute('id'),
            text: el.innerText
          }
        }
      )
    }
  }
);

const flatRefs = unformattedSections.reduce(
  (acc, sec) => acc.concat(
    [sec.section].concat(sec.subsections)
  ), []
);
flatRefs.forEach(
  reference => {
    const text = (reference.subidx ? (reference.secidx + "." + reference.subidx) :
    (reference.secidx));
    const className = reference.subidx ? "sub-title-number" : "title-number";
    reference.element.innerHTML = "<a href=\"#toc\" class=\"" + className +"\">" + text + ".</a> " + reference.text;
  }
);

Object.values(document.getElementsByClassName('secref'))
.forEach(
  reference => {
    const refId = reference.getAttribute('class').split(' ')[1];
    const rs = flatRefs.find(
      r => r.id === refId
    );
    const link = rs.subidx ? ("subsec-" + rs.secidx + "-" + rs.subidx) :
    ("sec-" + rs.secidx);
    const text = rs.subidx ? (rs.secidx + "." + rs.subidx) :
    (rs.secidx);
    reference.innerHTML = "<a href=\"#" + link + "\">" + text + "</a>";
  }
);

unformattedSections.forEach(
  section => {
    section.section.element.setAttribute("id", "sec-" + section.section.secidx);
    section.subsections.forEach(
      subsection => {
        subsection.element.setAttribute(
          "id", "subsec-" + subsection.secidx + "-" + subsection.subidx
        );
      }
    )
  }
);

const sections = unformattedSections.map(
  section => {
    return {
      section: formatSection(section.section),
      subsections: section.subsections.map(
        subsection => formatSection(subsection)
      )
    };
  }
);

ReactDOM.render(
  React.createElement(TOC, {
    sections: sections
  }),
  document.querySelector("#toc")
);
