import type { Actions } from './$types';
import { fail } from '@sveltejs/kit'
import { writeFileSync } from 'fs';

const sendToServer = true;

export const actions = {
    default: async ({ request }) => {
        if (!sendToServer) {
            // write the file to local dir
            const formData = Object.fromEntries(await request.formData());

            if (!(formData.fileToUpload as File).name ||
                (formData.fileToUpload as File).name === 'undefined') {
                return fail(400, {
                    error: true,
                    message: 'You must provide a file to upload'
                })
            }

            const { fileToUpload } = formData as { fileToUpload: File };

            writeFileSync(`static/${fileToUpload.name}`, Buffer.from(await fileToUpload.arrayBuffer()));

        } else {
            const uploadFormData = await request.formData();
            const response = await fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: uploadFormData,
            });

            if (response.ok) {
                console.log("File uploaded successfully!");
            } else {
                console.error("Failed to upload file: ", await response.text());
            }
        }
    }

} satisfies Actions;
