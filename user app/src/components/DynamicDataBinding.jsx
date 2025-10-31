import { useState } from "react";

const isObject = (val) => val && typeof val === "object" && !Array.isArray(val);

export function DynamicDataBinding({ data, level = 0 }) {
  if (!data || typeof data !== "object") return null;

  return (
    <div className="space-y-3">
      {Object.entries(data).map(([key, value]) => (
        <DataItem key={key} label={key} value={value} level={level} />
      ))}
    </div>
  );
}

const DataItem = ({ label, value, level }) => {
  const [open, setOpen] = useState(false);
  const readableLabel = label
    .replace(/_/g, " ")
    .replace(/\b\w/g, (l) => l.toUpperCase());
  const indent = `pl-${Math.min(level * 4, 12)}`;
  const toggle = () => setOpen((prev) => !prev);

  const isEmptyObject = (obj) =>
    obj &&
    typeof obj === "object" &&
    !Array.isArray(obj) &&
    Object.keys(obj).length === 0;

  const isEmptyArray = (arr) =>
    arr.length === 0 ||
    arr.every(
      (item) =>
        item === null ||
        item === undefined ||
        (typeof item === "string" && item.trim() === "") ||
        (typeof item === "object" && Object.keys(item).length === 0)
    );

  // 🔴 Show message if object is empty
  if (isObject(value) && isEmptyObject(value)) {
    return (
      <div
        className={`bg-white border rounded p-4 shadow-sm text-sm text-red-600 ${indent}`}
      >
        <strong>{readableLabel}:</strong> No content available.
      </div>
    );
  }

  // 🔴 Show message if array is empty or meaningless
  if (Array.isArray(value) && isEmptyArray(value)) {
    return (
      <div
        className={`bg-white border rounded p-4 shadow-sm text-sm text-red-600 ${indent}`}
      >
        <strong>{readableLabel}:</strong> No content available.
      </div>
    );
  }

  // ✅ Array with data
  if (Array.isArray(value)) {
    return (
      <div className={`bg-white border rounded p-4 shadow-md ${indent}`}>
        <div
          className="flex justify-between items-center cursor-pointer text-sm font-medium text-[#F68D1E]"
          onClick={toggle}
        >
          <span className="hover:underline">{readableLabel}</span>
          <span className="text-lg">{open ? "▼" : "▶"}</span>
        </div>
        {open && (
          <ul className="mt-3 pl-5 list-disc space-y-1 text-sm text-gray-800 max-h-60 overflow-y-auto pr-2">
            {value.map((item, idx) => (
              <li key={idx}>
                {isObject(item) ? (
                  <DynamicDataBinding data={item} level={level + 1} />
                ) : (
                  item?.toString()
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  // ✅ Object with data
  if (isObject(value)) {
    return (
      <div className={`bg-white border rounded p-4 shadow-md ${indent}`}>
        <div
          className="flex justify-between items-center cursor-pointer text-sm font-medium text-[#F68D1E] "
          onClick={toggle}
        >
          <span className="hover:underline">{readableLabel}</span>
          <span className="text-lg">{open ? "▼" : "▶"}</span>
        </div>
        {open && (
          <div className="mt-3 pl-2 text-sm text-gray-800 border-l border-gray-200 ml-1">
            <DynamicDataBinding data={value} level={level + 1} />
          </div>
        )}
      </div>
    );
  }

  // ✅ Primitive value
  return (
    <div className={`bg-white border rounded p-4 shadow-sm text-sm ${indent}`}>
      <strong className="text-gray-700">{readableLabel}:</strong>{" "}
      <span className="text-gray-600">{value?.toString() || "N/A"}</span>
    </div>
  );
};
