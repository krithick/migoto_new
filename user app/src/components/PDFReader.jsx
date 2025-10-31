import { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/esm/Page/TextLayer.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";

const PDFReader = (props) => {
  const [numPages, setNumPages] = useState(null);
  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }
  const { pdf } = props;

  // pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/legacy/build/pdf.worker.min.js`;
  // /pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;
  pdfjs.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69/pdf.worker.min.mjs";

  // pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  //   // "npm:pdfjs-dist/build/pdf.worker.min.mjs",
  //   // "pdfjs-dist/legacy/build/pdf.worker.min.mjs",
  //   "pdfjs-dist/build/pdf.worker.min.mjs",
  //   import.meta.url
  // ).toString();

  return (
    <Document
      file={pdf}
      // options={{ worker: "/pdf.worker.js" }}
      onLoadSuccess={onDocumentLoadSuccess}
      onLoadError={console.error}
    >
      {Array.from(new Array(numPages), (el, index) => (
        <Page scale={0.65} key={`page_${index + 1}`} pageNumber={index + 1} />
      ))}
    </Document>
  );
};

export default PDFReader;
