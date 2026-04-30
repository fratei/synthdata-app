"""Azure Blob Storage integration for SynthData dataset storage."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from ..config import get_settings

logger = logging.getLogger(__name__)


def get_blob_service_client():
    """Create an Azure Blob Storage client from environment config.

    Returns None if credentials are not configured.
    """
    settings = get_settings()

    if not settings.AZURE_STORAGE_CONNECTION_STRING:
        logger.warning(
            "Azure Storage not configured — set AZURE_STORAGE_CONNECTION_STRING"
        )
        return None

    try:
        from azure.storage.blob import BlobServiceClient
    except ImportError:
        logger.error(
            "azure-storage-blob package not installed. "
            "Install with: pip install azure-storage-blob"
        )
        return None

    return BlobServiceClient.from_connection_string(
        settings.AZURE_STORAGE_CONNECTION_STRING
    )


async def upload_dataset(
    data: bytes,
    dataset_id: str,
    file_format: str = "json",
    metadata: dict[str, Any] | None = None,
) -> str:
    """Upload a generated dataset to Azure Blob Storage.

    Args:
        data: Raw file bytes to upload.
        dataset_id: Unique identifier for the dataset.
        file_format: File extension (json, csv, parquet).
        metadata: Optional metadata to attach to the blob.

    Returns:
        The blob URL for downloading the dataset.
    """
    settings = get_settings()
    client = get_blob_service_client()

    if client is None:
        logger.warning("Blob client not available — returning placeholder URL")
        return f"https://synthdata.blob.core.windows.net/{settings.AZURE_STORAGE_CONTAINER}/{dataset_id}.{file_format}"

    container_client = client.get_container_client(settings.AZURE_STORAGE_CONTAINER)
    blob_name = f"{dataset_id}.{file_format}"

    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(
        data,
        overwrite=True,
        metadata=metadata or {},
    )

    logger.info("Uploaded dataset %s to blob storage", blob_name)
    return blob_client.url


async def generate_download_url(
    dataset_id: str,
    file_format: str = "json",
    expiry_hours: int = 24,
) -> str:
    """Generate a time-limited SAS URL for downloading a dataset.

    Args:
        dataset_id: Dataset identifier.
        file_format: File extension.
        expiry_hours: Number of hours the URL remains valid.

    Returns:
        A SAS URL for the dataset blob.
    """
    settings = get_settings()
    client = get_blob_service_client()

    if client is None:
        return f"https://synthdata.blob.core.windows.net/{settings.AZURE_STORAGE_CONTAINER}/{dataset_id}.{file_format}"

    try:
        from azure.storage.blob import BlobSasPermissions, generate_blob_sas
    except ImportError:
        return ""

    blob_name = f"{dataset_id}.{file_format}"
    sas_token = generate_blob_sas(
        account_name=client.account_name,
        container_name=settings.AZURE_STORAGE_CONTAINER,
        blob_name=blob_name,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=expiry_hours),
    )

    return f"{client.url}{settings.AZURE_STORAGE_CONTAINER}/{blob_name}?{sas_token}"
