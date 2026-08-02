import { Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { api, getErrorMessage } from "@/lib/api";

const confirmationPhrase = "DELETE TEST DATA";

export default function TestDataCleanup({ onDeleted }) {
  const [confirmation, setConfirmation] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const canDelete = confirmation === confirmationPhrase && !isDeleting;

  async function deleteTests(event) {
    event.preventDefault();
    if (!canDelete) return;
    setIsDeleting(true);
    try {
      const response = await api.post("/admin/inquiries/cleanup-test-data", { confirmation });
      toast.success(
        `${response.data.deleted_inquiries} inquiries, ${response.data.deleted_projects} projects, and ${response.data.deleted_media} media files deleted.`,
      );
      setConfirmation("");
      onDeleted();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <AlertDialog onOpenChange={(isOpen) => !isOpen && setConfirmation("")}>
      <AlertDialogTrigger asChild>
        <button className="cleanup-button" data-testid="open-test-cleanup-button" type="button">
          <Trash2 size={15} /> Remove test entries
        </button>
      </AlertDialogTrigger>
      <AlertDialogContent className="cleanup-dialog" data-testid="test-cleanup-dialog">
        <AlertDialogHeader>
          <AlertDialogTitle>Remove all test data?</AlertDialogTitle>
          <AlertDialogDescription>
            This permanently removes only marked QA inquiries, test portfolio projects, and
            linked test media. Real projects and client inquiries remain protected.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <label className="cleanup-label" htmlFor="cleanup-confirmation-input">
          Type <strong>{confirmationPhrase}</strong> to continue
          <input
            autoComplete="off"
            data-testid="test-cleanup-confirmation-input"
            id="cleanup-confirmation-input"
            onChange={(event) => setConfirmation(event.target.value)}
            spellCheck="false"
            value={confirmation}
          />
        </label>
        <AlertDialogFooter>
          <AlertDialogCancel data-testid="cancel-test-cleanup-button">Cancel</AlertDialogCancel>
          <AlertDialogAction
            className="cleanup-confirm-button"
            data-testid="confirm-test-cleanup-button"
            disabled={!canDelete}
            onClick={deleteTests}
          >
            {isDeleting ? "Removing…" : "Delete test entries"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}