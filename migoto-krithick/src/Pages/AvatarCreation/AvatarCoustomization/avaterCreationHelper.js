export function transformModels(input) {
    // Step 1: Group models by prefix
    const groupedByPrefix = {};

    input.forEach((item) => {
      // Extract prefix from the first model's filename (e.g., "Ama" from "Ama_Hair_Hr1.glb")
      const prefix = item?.models?.[0]?.original_filename?.split("_")[0] || "default";

      // Initialize array for this prefix if not exists
      if (!groupedByPrefix[prefix]) {
        groupedByPrefix[prefix] = [];
      }

      // Add item to the prefix group
      groupedByPrefix[prefix].push(item);
    });

    // Step 2: Transform into desired output format
    const result = Object.keys(groupedByPrefix).map((prefix) => {
      const models = [];
      const items = groupedByPrefix[prefix];

      // Filter out .glb files to process models
      const glbFiles = items[0]?.models?.filter((item) => item.original_filename?.endsWith(".glb")) || [];

      glbFiles.forEach((glb) => {
        // Find corresponding thumbnail (.png with same base name)
        const baseName = glb?.original_filename?.replace(".glb", "");
        const thumbnailItem = items[0]?.models.find((item) => item.original_filename === `${baseName}.png`);

        models.push({
          fileName: glb.original_filename,
          glb: glb.live_url,
          thumbnail: thumbnailItem ? thumbnailItem.live_url : "",
        });
      });

      return {
        name: prefix,
        models,
      };
    });
    return result;
  }// create structure to a model like
// [
//     {
//         "name": "Ama",
//         "models": [
//             {
//                 "fileName": "Ama_Armature.glb",
//                 "glb": "https://meta.novactech.in:7445/uploads/other/20250508060825_00020183.glb",
//                 "thumbnail": ""
//             },
//             {
//                 "fileName": "Ama_Body_B1.glb",
//                 "glb": "https://meta.novactech.in:7445/uploads/other/20250508060825_1c09253f.glb",
//                 "thumbnail": ""
//             },


  export  const groupModelConfigsByName = (configs) => {
    const grouped = {};

    configs.forEach((item) => {
      const match = item.original_filename.match(/^([^_]+)_/);
      if (!match) return;

      const name = match[1];

      if (!grouped[name]) {
        grouped[name] = {
          name,
          models: [],
        };
      }

      grouped[name].models.push(item);
    });

    return Object.values(grouped);
  }//   separate model based data in an array like 
// [
//     {
//         "name": "Ama",
//         "models": [
//             {
//                 "original_filename": "Ama_Armature.glb",
//                 "file_type": "model",
//                 "mime_type": "application/octet-stream",
//                 "file_size": 1258520,
//                 "local_url": "http://localhost:9000/uploads/other/20250508060825_00020183.glb",
//                 "live_url": "https://meta.novactech.in:7445/uploads/other/20250508060825_00020183.glb",
//                 "description": "string",
//                 "id": "39720deb-ca62-49ca-a3cd-42db96a454e1",
//                 "created_by": "66e0ed9d-2564-4af5-b2b6-d03a8984cdf6",
//                 "created_at": "2025-05-08T06:08:25.474000",
//                 "updated_at": "2025-05-08T06:08:25.474000"
//             },
//             {
//                 "original_filename": "Ama_Body_B1.glb",
//                 "file_type": "model",
//                 "mime_type": "application/octet-stream",
//                 "file_size": 2761208,
//                 "local_url": "http://localhost:9000/uploads/other/20250508060825_1c09253f.glb",
//                 "live_url": "https://meta.novactech.in:7445/uploads/other/20250508060825_1c09253f.glb",
//                 "description": "string",
//                 "id": "2bcbe6b4-65c8-45ae-863d-89f1f0f27036",
//                 "created_by": "66e0ed9d-2564-4af5-b2b6-d03a8984cdf6",
//                 "created_at": "2025-05-08T06:08:25.520000",
//                 "updated_at": "2025-05-08T06:08:25.520000"
//             },
//             {
//                 "original_filename": "Ama_Glass_Gls1.glb",
//                 "file_type": "model",
//                 "mime_type": "application/octet-stream",
//                 "file_size": 394960,
//                 "local_url": "http://localhost:9000/uploads/other/20250508060825_19470212.glb",
//                 "live_url": "https://meta.novactech.in:7445/uploads/other/20250508060825_19470212.glb",
//                 "description": "string",
//                 "id": "265fbc98-440f-4c02-86a0-2230fd780e62",
//                 "created_by": "66e0ed9d-2564-4af5-b2b6-d03a8984cdf6",
//                 "created_at": "2025-05-08T06:08:25.531000",
//                 "updated_at": "2025-05-08T06:08:25.531000"
//             },
