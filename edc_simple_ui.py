#!/usr/bin/env python3
"""
EDC Simple UI - Streamlit based EDC operations interface
=======================================================

This application provides a simple interface for EDC operations:
- Create Asset
- Create Policy  
- Create Contract Offer
- Fetch Catalog
- Data Transfer
"""

import streamlit as st
import requests
import json
import time
import os
from typing import Dict, Any, Optional

# EDC endpoints (Single connector for both provider and consumer operations)
EDC_MANAGEMENT = "http://edc-connector:19193"
EDC_PROTOCOL = "http://edc-connector:19194/protocol"

# Environment variables
PARTICIPANT_ID = os.getenv("PARTICIPANT_ID", "sample-participant-1.handson.dataspace.internal")
PARTICIPANT_FQDN = os.getenv("PARTICIPANT_FQDN", "sample-participant-1.handson.dataspace.internal")

def init_page():
    """Initialize Streamlit page configuration"""
    st.set_page_config(
        page_title="EDC Simple Operations",
        page_icon="🔗",
        layout="wide"
    )
    
    st.title("🔗 EDC Simple Operations UI")
    
    # Display participant information (vertically aligned)
    st.info(f"🏢 **Your Participant ID:** `{PARTICIPANT_ID}`")
    st.info(f"🌐 **Your FQDN:** `{PARTICIPANT_FQDN}`")
    
    # Debug mode control
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    
    with st.sidebar:
        st.header("⚙️ Settings")
        st.session_state.debug_mode = st.checkbox("🔧 Debug Mode", value=st.session_state.debug_mode)
        if st.session_state.debug_mode:
            st.caption("Debug information will be displayed")
    
    st.markdown("---")

def get_assets():
    """Get list of assets"""
    try:
        response = requests.post(
            f"{EDC_MANAGEMENT}/management/v3/assets/request",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "password"
            },
            json={
                "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
                "@type": "QuerySpec"
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

def get_policies():
    """Get list of policies"""
    try:
        response = requests.post(
            f"{EDC_MANAGEMENT}/management/v3/policydefinitions/request",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "password"
            },
            json={
                "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
                "@type": "QuerySpec"
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

def get_contract_definitions():
    """Get list of contract definitions"""
    try:
        response = requests.post(
            f"{EDC_MANAGEMENT}/management/v3/contractdefinitions/request",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "password"
            },
            json={
                "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
                "@type": "QuerySpec"
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

def create_asset():
    """Create Asset section"""
    st.header("📦 Create Asset")
    
    # Input section
    st.subheader("📦 Create New Asset")
    st.markdown("""
    この工程では、 データプロバイダーとして公開するデジタルアセット（データ、API、ファイルなど）をEDCカタログに登録します。
    アセットには一意のIDと、実際のデータソースへのアクセス情報（DataAddress）が含まれます。
    """)
    
    asset_id = st.text_input("Asset ID", value="sample-asset-1", key="asset_id")
    asset_name = st.text_input("Asset Name", value="Sample Asset", key="asset_name")
    asset_description = st.text_area("Description", value="Sample description", key="asset_desc")
    
    data_url = st.text_input("Data URL", value=f"http://{PARTICIPANT_FQDN}:8000/files/list", key="data_url")
    
    if st.button("Create Asset", type="primary"):
            payload = {
                "@context": {
                    "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
                },
                "@type": "Asset",
                "@id": asset_id,
                "properties": {
                    "name": asset_name,
                    "description": asset_description
                },
                "dataAddress": {
                    "@type": "DataAddress",
                    "type": "HttpData",
                    "baseUrl": data_url
                }
            }
            
            try:
                response = requests.post(
                    f"{EDC_MANAGEMENT}/management/v3/assets",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": "password"
                    },
                    json=payload,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    st.success("✅ Asset created successfully!")
                    if st.session_state.debug_mode:
                        st.info("🔧 Debug - Payload sent:")
                        st.json(payload)
                else:
                    st.error(f"❌ Failed to create asset: {response.status_code}")
                    
                    # Enhanced error message display
                    error_text = response.text
                    st.error(f"**HTTP Status:** {response.status_code}")
                    st.error(f"**Error Details:** {error_text}")
                    
                    # Check for specific error patterns
                    if "already exists" in error_text.lower() or "duplicate" in error_text.lower():
                        st.warning("🔄 **重複エラー**: このアセットIDは既に存在しています。別のIDを使用してください。")
                    elif "invalid" in error_text.lower():
                        st.warning("⚠️ **検証エラー**: 入力されたデータが無効です。各フィールドを確認してください。")
                    elif "url" in error_text.lower() and "malformed" in error_text.lower():
                        st.warning("🔗 **URL エラー**: データURLの形式が正しくありません。")
                    
                    if st.session_state.debug_mode:
                        st.error(f"**Full Response:** {error_text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    # Current Assets section
    st.markdown("---")
    st.subheader("📋 Current Assets")
    assets = get_assets()
    if assets:
        for asset in assets:
            asset_info = asset.get('properties', {})
            st.write(f"**{asset.get('@id', 'N/A')}** - {asset_info.get('name', 'No name')}")
    else:
        st.info("No assets found")

def create_policy():
    """Create Policy section"""
    st.header("📋 Create Policy")
    
    # Input section
    st.subheader("📜 Create New Policy")
    st.markdown("""
    この工程では、 アセットへのアクセス条件を定義するポリシーを作成します。
    参加者ID制約を設定することで、特定の参加者のみがアセットにアクセスできるよう制限できます。
    """)
    
    policy_id = st.text_input("Policy ID", value="allow-all-policy", key="policy_id")
    
    # Participant ID constraint option
    use_participant_constraint = st.checkbox("Restrict to specific Participant ID", key="use_participant_constraint")
    participant_id = ""
    if use_participant_constraint:
        participant_id = st.text_input("Allowed Participant ID", 
                                         placeholder=f"e.g., sample-participant-2.handson.dataspace.internal", 
                                         key="allowed_participant_id")
    
    if st.button("Create Policy", type="primary"):
            # Build policy permissions based on constraints
            permissions = []
            
            if use_participant_constraint and participant_id:
                # Add participant ID constraint
                permissions = [{
                    "odrl:action": "USE",
                    "odrl:constraint": {
                        "@type": "AtomicConstraint",
                        "odrl:leftOperand": "https://w3id.org/edc/v0.0.1/ns/participantId",
                        "odrl:operator": {
                            "@id": "odrl:eq"
                        },
                        "odrl:rightOperand": participant_id
                    }
                }]
            else:
                # No constraints - allow all
                permissions = [{
                    "odrl:action": "USE"
                }]

            payload = {
                "@context": {
                    "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
                    "odrl": "http://www.w3.org/ns/odrl/2/"
                },
                "@type": "PolicyDefinition",
                "@id": policy_id,
                "policy": {
                    "@context": "http://www.w3.org/ns/odrl.jsonld",
                    "@type": "http://www.w3.org/ns/odrl/2/Set",
                    "odrl:permission": permissions,
                    "odrl:prohibition": [],
                    "odrl:obligation": []
                }
            }
            
            try:
                response = requests.post(
                    f"{EDC_MANAGEMENT}/management/v3/policydefinitions",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": "password"
                    },
                    json=payload,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    st.success("✅ Policy created successfully!")
                    if st.session_state.debug_mode:
                        st.info("🔧 Debug - Policy payload:")
                        st.json(payload)
                else:
                    st.error(f"❌ Failed to create policy: {response.status_code}")
                    
                    # Enhanced error message display
                    error_text = response.text
                    st.error(f"**HTTP Status:** {response.status_code}")
                    st.error(f"**Error Details:** {error_text}")
                    
                    # Check for specific error patterns
                    if "already exists" in error_text.lower() or "duplicate" in error_text.lower():
                        st.warning("🔄 **重複エラー**: このポリシーIDは既に存在しています。別のIDを使用してください。")
                    elif "invalid" in error_text.lower():
                        st.warning("⚠️ **検証エラー**: ポリシー定義が無効です。制約条件を確認してください。")
                    elif "participant" in error_text.lower():
                        st.warning("👤 **参加者IDエラー**: 指定された参加者IDの形式が正しくない可能性があります。")
                    
                    if st.session_state.debug_mode:
                        st.error(f"**Full Response:** {error_text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    # Current Policies section
    st.markdown("---")
    st.subheader("📋 Current Policies")
    policies = get_policies()
    if policies:
        for policy in policies:
            policy_name = policy.get('@id', 'N/A')
            # Check if policy has participant constraints
            policy_obj = policy.get('policy', {})
            permissions = policy_obj.get('odrl:permission', [])
            has_constraint = any(
                perm.get('odrl:constraint', {}).get('odrl:leftOperand') == 'https://w3id.org/edc/v0.0.1/ns/participantId'
                for perm in permissions if isinstance(perm, dict)
            )
            constraint_info = " 🔒 (Participant restricted)" if has_constraint else ""
            st.write(f"**{policy_name}**{constraint_info}")
    else:
        st.info("No policies found")
    
    st.markdown("---")
    st.subheader("💡 Policy Types")
    st.write("- **Allow All**: No restrictions")  
    st.write("- **Participant Restricted** 🔒: Only specific participant can access")

def create_contract_offer():
    """Create Contract Offer section"""
    st.header("📄 Create Contract Offer")
    st.markdown("""
    この工程では、 作成したアセットとポリシーを組み合わせて、データ交換の契約条件を定義したコントラクトオファーを作成します。
    これにより、他の参加者があなたのデータカタログでオファーを発見し、契約交渉を開始できるようになります。
    """)
    
    # Input section
    st.subheader("Create New Contract Definition")
    contract_id = st.text_input("Contract Definition ID", value="contract-def-1", key="contract_id")
    
    # Get available assets and policies for dropdowns
    assets = get_assets()
    policies = get_policies()
    
    asset_ids = [asset.get('@id', '') for asset in assets] if assets else ['sample-asset-1']
    policy_ids = [policy.get('@id', '') for policy in policies] if policies else ['allow-all-policy']
    
    selected_asset = st.selectbox("Select Asset", asset_ids, key="selected_asset")
    access_policy = st.selectbox("Access Policy", policy_ids, key="access_policy")
    contract_policy = st.selectbox("Contract Policy", policy_ids, key="contract_policy")
    
    if st.button("Create Contract Definition", type="primary"):
            payload = {
                "@context": {
                    "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
                },
                "@type": "ContractDefinition",
                "@id": contract_id,
                "accessPolicyId": access_policy,
                "contractPolicyId": contract_policy,
                "assetsSelector": [
                    {
                        "@type": "CriterionDto",
                        "operandLeft": "https://w3id.org/edc/v0.0.1/ns/id",
                        "operator": "=",
                        "operandRight": selected_asset
                    }
                ]
            }
            
            try:
                response = requests.post(
                    f"{EDC_MANAGEMENT}/management/v3/contractdefinitions",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": "password"
                    },
                    json=payload,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    st.success("✅ Contract definition created successfully!")
                    if st.session_state.debug_mode:
                        st.info("🔧 Debug - Contract Definition payload:")
                        st.json(payload)
                else:
                    st.error(f"❌ Failed to create contract definition: {response.status_code}")
                    
                    # Enhanced error message display
                    error_text = response.text
                    st.error(f"**HTTP Status:** {response.status_code}")
                    st.error(f"**Error Details:** {error_text}")
                    
                    # Check for specific error patterns
                    if "already exists" in error_text.lower() or "duplicate" in error_text.lower():
                        st.warning("🔄 **重複エラー**: この契約定義IDは既に存在しています。別のIDを使用してください。")
                    elif "not found" in error_text.lower():
                        st.warning("🔍 **参照エラー**: 指定されたアセットまたはポリシーが見つかりません。先にアセットとポリシーを作成してください。")
                    elif "invalid" in error_text.lower():
                        st.warning("⚠️ **検証エラー**: 入力されたデータが無効です。各フィールドを確認してください。")
                    
                    if st.session_state.debug_mode:
                        st.error(f"**Full Response:** {error_text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    # Current Contract Definitions section
    st.markdown("---")
    st.subheader("📋 Current Contract Definitions (Offers)")
    
    contract_definitions = get_contract_definitions()
    if contract_definitions:
        st.info(f"✅ Found {len(contract_definitions)} contract definition(s)")
        
        for idx, contract_def in enumerate(contract_definitions):
            contract_id = contract_def.get('@id', 'N/A')
            access_policy_id = contract_def.get('accessPolicyId', 'N/A')
            contract_policy_id = contract_def.get('contractPolicyId', 'N/A')
            
            # Get asset selector info
            assets_selector = contract_def.get('assetsSelector', [])
            asset_ids = []
            for selector in assets_selector:
                if isinstance(selector, dict):
                    if selector.get('operandLeft') == 'https://w3id.org/edc/v0.0.1/ns/id':
                        asset_ids.append(selector.get('operandRight', 'Unknown'))
            
            with st.expander(f"📄 Contract Definition {idx + 1}: {contract_id}"):
                st.write(f"**Access Policy:** `{access_policy_id}`")
                st.write(f"**Contract Policy:** `{contract_policy_id}`")
                if asset_ids:
                    st.write(f"**Assets:** `{', '.join(asset_ids)}`")
                else:
                    st.write("**Assets:** No specific assets selected")
                
                # Show creation timestamp if available
                created_at = contract_def.get('createdAt')
                if created_at:
                    st.write(f"**Created:** {created_at}")
                
                if st.session_state.debug_mode:
                    st.json(contract_def)
    else:
        st.info("No contract definitions found")
    
    st.markdown("---")
    st.subheader("💡 Contract Definition Status")
    st.write("- Contract definitionsは他の参加者がカタログで発見できるオファーです")  
    st.write("- 各定義には特定のアセット、アクセスポリシー、契約ポリシーが含まれます")
    
    # Available Resources section
    st.markdown("---")
    st.subheader("📋 Available Resources")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("**Assets:**")
        for asset_id in asset_ids:
            st.write(f"- {asset_id}")
    with col2:
        st.write("**Policies:**")
        for policy_id in policy_ids:
            st.write(f"- {policy_id}")

def evaluate_policy_for_participant(policy_obj, participant_id):
    """Evaluate if a policy allows access for the given participant ID"""
    if not policy_obj or not participant_id:
        return True, "No policy constraints"
    
    # permissionは単一オブジェクトの場合もあるし、配列の場合もある
    permissions_raw = policy_obj.get("odrl:permission", [])
    if isinstance(permissions_raw, dict):
        # 単一オブジェクトの場合は配列にラップ
        permissions = [permissions_raw]
    elif isinstance(permissions_raw, list):
        permissions = permissions_raw
    else:
        return True, "No permissions defined"
    
    if not permissions:
        return True, "No permissions defined"
    
    def check_constraint(constraint):
        """制約をチェックするヘルパー関数"""
        left_operand = constraint.get("odrl:leftOperand")
        operator = constraint.get("odrl:operator", {})
        right_operand = constraint.get("odrl:rightOperand")
        
        # left_operandがオブジェクト形式の場合、@idを取得
        if isinstance(left_operand, dict):
            left_operand_value = left_operand.get("@id", "")
        else:
            left_operand_value = left_operand
        
        # operatorがオブジェクト形式の場合、@idを取得
        if isinstance(operator, dict):
            operator_value = operator.get("@id", "")
        else:
            operator_value = operator
        
        # participantId制約をチェック（複数の形式に対応）
        participant_id_patterns = [
            "https://w3id.org/edc/v0.0.1/ns/participantId",
            "edc:participantId", 
            "participantId"
        ]
        
        if left_operand_value in participant_id_patterns:
            if operator_value in ["odrl:eq", "EQ", "eq"]:
                if right_operand == participant_id:
                    return True, f"✅ Participant ID matches: {right_operand}"
                else:
                    return False, f"❌ Participant ID mismatch. Required: {right_operand}, Your ID: {participant_id}"
        
        return None, None
    
    for permission in permissions:
        if isinstance(permission, dict):
            # 単一制約の場合
            constraint = permission.get("odrl:constraint", {})
            if constraint:
                result, message = check_constraint(constraint)
                if result is not None:
                    return result, message
            
            # 複数制約の場合（constraintsが配列）
            constraints = permission.get("odrl:constraints", [])
            if not constraints:
                constraints = permission.get("constraints", [])
            
            for constraint in constraints:
                result, message = check_constraint(constraint)
                if result is not None:
                    return result, message
    
    return True, "No participant constraints found"

def fetch_catalog():
    """Fetch Catalog section"""
    st.header("🗂️ Fetch Catalog")
    st.markdown("""
    この工程では、 他の参加者（プロバイダー）が公開しているデータカタログから利用可能なコントラクトオファーを取得し、利用可能なアセットとその契約条件を確認します。
    ポリシー評価により、あなたの参加者IDでアクセス可能なオファーのみが表示されます。
    """)
    
    # Use environment variable for participant ID
    consumer_participant_id = PARTICIPANT_ID
    if st.session_state.debug_mode:
        st.info(f"🔍 **Evaluating policies for:** `{consumer_participant_id}`")
    
    provider_fqdn = st.text_input("Provider FQDN", 
                                  placeholder="e.g., sample-participant-2.handson.dataspace.internal", 
                                  key="provider_fqdn")
    
    # Provider Participant ID (通常はFQDNと同じ値)
    provider_participant_id = st.text_input("Provider Participant ID",
                                           value=provider_fqdn,
                                           placeholder="e.g., sample-participant-2.handson.dataspace.internal",
                                           help="通常はFQDNと同じ値を使用します",
                                           key="provider_participant_id")
    
    if st.button("Fetch Catalog", type="primary"):
        # Trim whitespace from input
        provider_fqdn = provider_fqdn.strip() if provider_fqdn else ""
        
        if not provider_fqdn:
            st.warning("Please enter a provider FQDN")
        else:
            # Construct DSP endpoint
            dsp_endpoint = f"http://{provider_fqdn}:19194/protocol"
            
            payload = {
                "@context": {
                    "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
                },
                "@type": "CatalogRequest",
                "counterPartyAddress": dsp_endpoint,
                "protocol": "dataspace-protocol-http",
                "querySpec": {
                    "@type": "QuerySpec"
                }
            }
            
            # Debug information
            if st.session_state.debug_mode:
                st.info(f"🔍 **Debug Info:**")
                st.json({
                    "provider_fqdn": provider_fqdn,
                    "dsp_endpoint": dsp_endpoint,
                    "consumer_id": consumer_participant_id,
                    "payload": payload
                })
                
                # Test with curl equivalent
                st.write("**🔧 Curl Equivalent:**")
                curl_cmd = f"""curl -X POST -H "Content-Type: application/json" -H "X-API-Key: password" -d '{json.dumps(payload)}' {EDC_MANAGEMENT}/management/v3/catalog/request"""
                st.code(curl_cmd, language="bash")
            
            try:
                if st.session_state.debug_mode:
                    st.write(f"**📤 Sending request to:** `{EDC_MANAGEMENT}/management/v3/catalog/request`")
                with st.spinner(f"Fetching catalog from {provider_fqdn}..."):
                    response = requests.post(
                        f"{EDC_MANAGEMENT}/management/v3/catalog/request",
                        headers={
                            "Content-Type": "application/json",
                            "X-API-Key": "password"
                        },
                        json=payload,
                        timeout=30
                    )
                
                if st.session_state.debug_mode:    
                    st.write(f"**📥 Response Status:** `{response.status_code}`")
                    st.write(f"**📥 Response Headers:** `{dict(response.headers)}`")
                    
                if response.status_code == 200:
                    catalog = response.json()
                    st.success(f"✅ Catalog fetched from {provider_fqdn}!")
                    
                    # セッション状態にProvider情報を保存（ウィジェットキーと異なる名前を使用）
                    st.session_state['cached_provider_fqdn'] = provider_fqdn.strip()
                    st.session_state['cached_provider_participant_id'] = provider_participant_id.strip()
                    st.session_state['last_catalog_data'] = catalog
                    
                    # Display datasets with policy evaluation
                    datasets_raw = catalog.get("dcat:dataset", [])
                    # Handle both single dataset object and array of datasets
                    if isinstance(datasets_raw, dict):
                        datasets = [datasets_raw]
                    elif isinstance(datasets_raw, list):
                        datasets = datasets_raw
                    else:
                        datasets = []
                    
                    if datasets:
                        # First pass: filter datasets and offers based on policy evaluation
                        accessible_datasets = []
                        blocked_datasets = []
                        
                        for dataset in datasets:
                            dataset_id = dataset.get('@id', 'Unknown ID')
                            dataset_name = dataset.get('dcat:keyword', [])
                            
                            # Check contract offers for this dataset
                            offers_raw = dataset.get('odrl:hasPolicy', [])
                            # Handle both single offer object and array of offers
                            if isinstance(offers_raw, dict):
                                offers = [offers_raw]
                            elif isinstance(offers_raw, list):
                                offers = offers_raw
                            else:
                                offers = []
                            
                            accessible_offers_for_dataset = []
                            blocked_offers_for_dataset = []
                            
                            for offer in offers:
                                can_access, evaluation_msg = evaluate_policy_for_participant(
                                    offer, consumer_participant_id
                                )
                                
                                if can_access:
                                    accessible_offers_for_dataset.append({
                                        'offer': offer,
                                        'evaluation_msg': evaluation_msg
                                    })
                                else:
                                    blocked_offers_for_dataset.append({
                                        'offer': offer,
                                        'evaluation_msg': evaluation_msg
                                    })
                            
                            # Only include dataset if it has at least one accessible offer
                            if accessible_offers_for_dataset:
                                accessible_datasets.append({
                                    'dataset': dataset,
                                    'accessible_offers': accessible_offers_for_dataset,
                                    'blocked_offers': blocked_offers_for_dataset
                                })
                            else:
                                blocked_datasets.append({
                                    'dataset': dataset,
                                    'blocked_offers': blocked_offers_for_dataset
                                })
                        
                        # Display accessible datasets
                        if accessible_datasets:
                            st.subheader(f"✅ Accessible Datasets ({len(accessible_datasets)})")
                            
                            for idx, dataset_info in enumerate(accessible_datasets):
                                dataset = dataset_info['dataset']
                                dataset_id = dataset.get('@id', 'Unknown ID')
                                dataset_name = dataset.get('dcat:keyword', [])
                                accessible_offers = dataset_info['accessible_offers']
                                blocked_offers = dataset_info['blocked_offers']
                                
                                with st.expander(f"📦 Dataset {idx + 1}: {dataset_id}"):
                                    if dataset_name:
                                        st.write(f"**Keywords:** {', '.join(dataset_name)}")
                                    
                                    # Show accessible offers
                                    st.write(f"**✅ Accessible Contract Offers:** {len(accessible_offers)}")
                                    for offer_idx, offer_info in enumerate(accessible_offers):
                                        offer = offer_info['offer']
                                        evaluation_msg = offer_info['evaluation_msg']
                                        offer_id = offer.get('@id', f'offer-{offer_idx}')
                                        
                                        st.write(f"🔗 **Offer ID:** `{offer_id}`")
                                        st.success(f"**Policy Evaluation:** {evaluation_msg}")
                                        
                                        # Evaluate policy for consumer in debug mode
                                        if st.session_state.get("debug_mode"):
                                            st.write("**🔍 Policy Debug - Offer Structure:**")
                                            st.json(offer)
                                        
                                        # Store offer info in session state for data transfer
                                        if 'accessible_offers' not in st.session_state:
                                            st.session_state['accessible_offers'] = {}
                                        st.session_state['accessible_offers'][offer_id] = {
                                            'dataset_id': dataset_id,
                                            'provider_fqdn': provider_fqdn,
                                            'dsp_endpoint': dsp_endpoint,
                                            'offer_policy': offer  # カタログから取得したoffer全体を保存
                                        }
                                    
                                    # Show blocked offers if any (only in debug mode)
                                    if blocked_offers and st.session_state.get("debug_mode"):
                                        st.write(f"**❌ Blocked Contract Offers:** {len(blocked_offers)} (Debug)")
                                        for offer_idx, offer_info in enumerate(blocked_offers):
                                            offer = offer_info['offer']
                                            evaluation_msg = offer_info['evaluation_msg']
                                            offer_id = offer.get('@id', f'blocked-offer-{offer_idx}')
                                            
                                            st.write(f"🚫 **Blocked Offer ID:** `{offer_id}`")
                                            st.error(f"**Policy Evaluation:** {evaluation_msg}")
                        
                        # Show blocked datasets summary (only if user has debug mode enabled)
                        if blocked_datasets and st.session_state.get("debug_mode"):
                            st.subheader(f"🚫 Blocked Datasets ({len(blocked_datasets)}) - Debug Mode")
                            st.info("以下のデータセットは、あなたの参加者IDでアクセス許可されていないため非表示になっています。")
                            
                            for idx, dataset_info in enumerate(blocked_datasets):
                                dataset = dataset_info['dataset']
                                dataset_id = dataset.get('@id', 'Unknown ID')
                                blocked_offers = dataset_info['blocked_offers']
                                
                                with st.expander(f"🚫 Blocked Dataset {idx + 1}: {dataset_id}"):
                                    st.write(f"**❌ All Offers Blocked:** {len(blocked_offers)}")
                                    for offer_idx, offer_info in enumerate(blocked_offers):
                                        offer = offer_info['offer']
                                        evaluation_msg = offer_info['evaluation_msg']
                                        offer_id = offer.get('@id', f'blocked-offer-{offer_idx}')
                                        
                                        st.write(f"🚫 **Blocked Offer ID:** `{offer_id}`")
                                        st.error(f"**Policy Evaluation:** {evaluation_msg}")
                        
                        elif blocked_datasets:
                            st.info(f"ℹ️ {len(blocked_datasets)} dataset(s) are not accessible with your participant ID.")
                        
                        # If no accessible datasets at all
                        if not accessible_datasets:
                            st.warning("❌ No datasets are accessible with your current participant ID.")
                            st.info("💡 Contact the data provider to get proper access permissions or check if your participant ID is correctly configured.")
                    else:
                        st.warning("No datasets found in catalog")
                else:
                    st.error(f"❌ Failed to fetch catalog: {response.status_code}")
                    st.write(f"**Response Headers:** {dict(response.headers)}")
                    st.text(f"**Response Body:** {response.text}")
                    st.write(f"**Request URL:** {EDC_MANAGEMENT}/management/v3/catalog/request")
            except Exception as e:
                st.error(f"❌ Error: {e}")


def negotiate_contract():
    """Contract Negotiation section"""
    st.header("🤝 Negotiate Contract")

    st.markdown("""
    この工程では、 カタログから選択したオファーに対して契約交渉を開始します。
    EDCは自動的にプロバイダーと契約交渉を行い、合意に達すると契約が確定されます。
    """)

    # Show provider information from session state
    cached_provider_participant_id = st.session_state.get('cached_provider_participant_id')
    cached_provider_fqdn = st.session_state.get('cached_provider_fqdn')
    if cached_provider_participant_id and cached_provider_fqdn:
        st.info(f"🏢 **Target Provider:** `{cached_provider_participant_id}` (FQDN: {cached_provider_fqdn})")
    else:
        st.warning("⚠️ Provider情報が見つかりません。まずCatalogをフェッチしてください。")

    # Show accessible offers from catalog fetch
    accessible_offers = st.session_state.get('accessible_offers', {})
    if accessible_offers:
        st.info(f"✅ {len(accessible_offers)} accessible offer(s) found from catalog")
        st.write("**💡 Offer ID説明:** これはProvider側が作成したContract Definitionの中のPolicy IDです")
        offer_options = list(accessible_offers.keys())
        selected_offer = st.selectbox("Select Accessible Offer", offer_options, key="selected_offer")
        offer_id = selected_offer

        # Show offer details
        if offer_id in accessible_offers:
            offer_info = accessible_offers[offer_id]
            st.write(f"**📋 選択されたOffer詳細:**")
            st.write(f"- **Dataset ID:** {offer_info.get('dataset_id')}")
            st.write(f"- **Provider FQDN:** {offer_info.get('provider_fqdn')}")
            st.write(f"- **DSP Endpoint:** {offer_info.get('dsp_endpoint')}")
    else:
        st.warning("No accessible offers found. Please fetch catalog first.")
        offer_id = st.text_input(
            "Manual Offer ID",
            key="manual_offer_id",
            help="Enter offer ID manually if needed"
        )

    if st.button("Start Contract Negotiation", key="negotiate"):
        if not offer_id:
            st.warning("Please provide an Offer ID")
            return

        # Get provider endpoint and offer info from accessible offers
        provider_endpoint = EDC_PROTOCOL  # fallback
        dataset_id = "sample-asset-1"     # fallback
        offer_policy = None

        if st.session_state.get("debug_mode"):
            st.write("**🔍 Debug - Contract Negotiation Target:**")

        if accessible_offers and offer_id in accessible_offers:
            offer_info = accessible_offers[offer_id]
            provider_endpoint = offer_info.get('dsp_endpoint', EDC_PROTOCOL)
            dataset_id = offer_info.get('dataset_id', 'sample-asset-1')
            offer_policy = offer_info.get('offer_policy')  # カタログから取得したoffer全体

            st.write(f"- **Provider FQDN**: `{offer_info.get('provider_fqdn')}`")
            st.write(f"- **Provider DSP Endpoint**: `{provider_endpoint}`")
            st.write(f"- **Dataset ID**: `{dataset_id}`")
        else:
            st.write(f"- **Fallback DSP Endpoint**: `{provider_endpoint}`")

        # カタログから取得したofferをクリーンアップしてEDC形式に変換
        if offer_policy:
            # デバッグ：カタログから取得した元のオファーを表示
            if st.session_state.get("debug_mode"):
                st.write("**🔍 Original Offer from Catalog:**")
                st.json(offer_policy)

            # カタログから適切な値を取得
            asset_name = None
            # セッション状態からProvider Participant IDを取得
            provider_participant_id = st.session_state.get('cached_provider_participant_id', 'Sample-Participant-2')

            # セッション状態からカタログデータを取得
            catalog_data = st.session_state.get('last_catalog_data')

            # カタログレスポンスからアセット名を取得
            if catalog_data and "dcat:dataset" in catalog_data:
                datasets_raw = catalog_data["dcat:dataset"]
                # Handle both single dataset object and array of datasets
                if isinstance(datasets_raw, dict):
                    datasets = [datasets_raw]
                elif isinstance(datasets_raw, list):
                    datasets = datasets_raw
                else:
                    datasets = []
                
                for dataset in datasets:
                    if isinstance(dataset, dict) and dataset.get("@id") == dataset_id:
                        asset_name = dataset.get("dct:title") or dataset.get("@id")
                        break

            # ODRLのprefixを除去して正規化
            def clean_odrl_prefixes(policy_data):
                """Remove ODRL prefixes and normalize policy structure"""
                if isinstance(policy_data, dict):
                    cleaned = {}
                    for key, value in policy_data.items():
                        clean_key = key.replace("odrl:", "") if key.startswith("odrl:") else key
                        if isinstance(value, (dict, list)):
                            cleaned[clean_key] = clean_odrl_prefixes(value)
                        else:
                            cleaned[clean_key] = value
                    return cleaned
                elif isinstance(policy_data, list):
                    return [clean_odrl_prefixes(item) for item in policy_data]
                else:
                    return policy_data

            # カタログから取得したオファーに不足フィールドを補完
            enhanced_policy = offer_policy.copy()
            
            # 必須フィールドを追加（不足している場合）
            if "odrl:assigner" not in enhanced_policy:
                enhanced_policy["odrl:assigner"] = {"@id": provider_participant_id}
            if "odrl:target" not in enhanced_policy:
                enhanced_policy["odrl:target"] = {"@id": dataset_id}
            
            payload = {
                "@context": {
                    "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
                    "edc": "https://w3id.org/edc/v0.0.1/ns/",
                    "odrl": "http://www.w3.org/ns/odrl/2/",
                    "dcat": "http://www.w3.org/ns/dcat#",
                    "dct": "http://purl.org/dc/terms/",
                    "dspace": "https://w3id.org/dspace/v0.8/"
                },
                "@type": "ContractRequest",
                "counterPartyAddress": provider_endpoint,
                "protocol": "dataspace-protocol-http",
                "policy": enhanced_policy
            }
        else:
            # フォールバック用のデフォルトオファー
            payload = {
                "@context": {
                    "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
                    "edc": "https://w3id.org/edc/v0.0.1/ns/",
                    "odrl": "http://www.w3.org/ns/odrl/2/",
                    "dcat": "http://www.w3.org/ns/dcat#",
                    "dct": "http://purl.org/dc/terms/",
                    "dspace": "https://w3id.org/dspace/v0.8/"
                },
                "@type": "ContractRequest",
                "counterPartyAddress": provider_endpoint,
                "protocol": "dataspace-protocol-http",
                "policy": {
                    "@id": offer_id,
                    "@type": "odrl:Offer",
                    "odrl:assigner": {"@id": provider_participant_id},
                    "odrl:target": {"@id": dataset_id},
                    "odrl:permission": [{"odrl:action": {"@id": "USE"}}],
                    "odrl:prohibition": [],
                    "odrl:obligation": []
                }
            }

        # Debug contract negotiation payload
        if st.session_state.get("debug_mode"):
            st.write("**🔧 Contract Negotiation Payload:**")
            st.json(payload)

        try:
            with st.spinner("Starting contract negotiation..."):
                response = requests.post(
                    f"{EDC_MANAGEMENT}/management/v3/contractnegotiations",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": "password"
                    },
                    json=payload,
                    timeout=30
                )

            if st.session_state.get("debug_mode"):
                st.write(f"**📥 Contract Negotiation Response Status:** `{response.status_code}`")

            if response.status_code in [200, 201]:
                negotiation_id = response.json().get("@id")
                st.success(f"✅ Contract negotiation started! ID: {negotiation_id}")
                st.session_state["negotiation_id"] = negotiation_id

                # Wait for negotiation to complete
                with st.spinner("Waiting for negotiation to complete..."):
                    for i in range(30):
                        time.sleep(2)
                        check_response = requests.get(
                            f"{EDC_MANAGEMENT}/management/v3/contractnegotiations/{negotiation_id}",
                            headers={
                                "Content-Type": "application/json",
                                "X-API-Key": "password"
                            },
                            timeout=20
                        )

                        if check_response.status_code == 200:
                            body = check_response.json()
                            state = body.get("state")
                            st.info(f"Negotiation state: {state}")

                            if state == "FINALIZED":
                                agreement_id = body.get("contractAgreementId")
                                st.success(f"✅ Contract finalized! Agreement ID: {agreement_id}")
                                st.session_state["agreement_id"] = agreement_id
                                break
                        else:
                            # 状態取得失敗時も少し待って再試行
                            if st.session_state.get("debug_mode"):
                                st.warning(f"State check failed (HTTP {check_response.status_code}) — retrying…")
            else:
                st.error(f"❌ Failed to start negotiation: {response.status_code}")
                st.text(response.text)
        except Exception as e:      
            st.error(f"❌ Error starting negotiation: {e}")


def data_transfer():
    """Data Transfer section"""
    st.header("📡 Data Transfer")
    
    st.markdown("""
    この工程では、 確定した契約合意を基にして実際のデータ転送プロセスを開始します。
    """)

    if "agreement_id" not in st.session_state:
        st.info("まず契約交渉（ネゴシエーション）を完了してください。")
        return

    st.info(f"Agreement ID: {st.session_state['agreement_id']}")

    if st.button("Start Data Transfer", key="transfer"):
        # ---- 事前準備 ----
        accessible_offers = st.session_state.get('accessible_offers', {})
        provider_endpoint = EDC_PROTOCOL  # fallback (例: "http://<provider-host>:19291")
        asset_id = "sample-asset-1"       # fallback

        # 利用可能なオファ情報から最初のものを使用
        for _, offer_info in accessible_offers.items():
            provider_endpoint = offer_info.get('dsp_endpoint', EDC_PROTOCOL)
            asset_id = offer_info.get('dataset_id', 'sample-asset-1')
            break  # 先頭のみ使用

        payload = {
            "@context": {"@vocab": "https://w3id.org/edc/v0.0.1/ns/"},
            "@type": "TransferRequest",
            "counterPartyAddress": provider_endpoint,
            "protocol": "dataspace-protocol-http",
            "contractId": st.session_state["agreement_id"],
            "assetId": asset_id,
            "transferType": "HttpData-PULL",
            "dataDestination": {
                "@type": "DataAddress",
                "type": "HttpProxy"
            }
        }

        transfer_id = None

        # ---- 転送開始 ----
        try:
            with st.spinner("Starting data transfer..."):
                response = requests.post(
                    f"{EDC_MANAGEMENT}/management/v3/transferprocesses",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": "password"
                    },
                    json=payload,
                    timeout=30
                )

            if response.status_code in [200, 201]:
                transfer_id = response.json().get("@id")
                st.success(f"✅ Data transfer started! ID: {transfer_id}")
            else:
                st.error(f"❌ Failed to start transfer: HTTP {response.status_code}")
                st.text(response.text)
                return  # 転送開始に失敗した場合は以降を中止
        except Exception as e:
            st.error(f"❌ Error starting transfer: {e}")
            return

        # ---- 転送状態確認をシンプル化 ----
        st.write("**⏳ Transfer started - waiting briefly before checking EDR...**")
        # 状態確認の代わりに短い待機時間を設ける（EDRは通常すぐに利用可能）
        time.sleep(3)
        st.info("✅ Proceeding to EDR retrieval...")

        # ---- EDR 取得（ポーリング）----
        endpoint = None
        auth_header = None



        # サンプルに基づく正しいEDR取得方法
        st.write("**🔗 Getting Endpoint Data Reference (EDR)...**")
        
        endpoint = None
        auth_header = None
        
        with st.spinner("Getting EDR from transfer process..."):
            for attempt in range(1, 16):  # 最大30秒（2秒 x 15）
                try:
                    time.sleep(2)
                    # サンプルに記載されている正しい方法: GET /management/v3/edrs/<transfer process id>/dataaddress
                    edr_response = requests.get(
                        f"{EDC_MANAGEMENT}/management/v3/edrs/{transfer_id}/dataaddress",
                        headers={
                            "Content-Type": "application/json",
                            "X-API-Key": "password"
                        },
                        timeout=20
                    )
                    
                    if edr_response.status_code == 200:
                        edr = edr_response.json()
                        st.success("✅ EDR (Endpoint Data Reference) obtained!")
                        if st.session_state.get("debug_mode"):
                            st.json(edr)

                        endpoint = edr.get("endpoint")
                        # サンプルに記載: "authorization"フィールドを使用
                        auth_header = edr.get("authorization")

                        if endpoint and auth_header:
                            # 環境変数プレースホルダーの処理
                            if "${EDC_DATAPLANE_PUBLIC_URL:" in endpoint and "}" in endpoint:
                                # ${EDC_DATAPLANE_PUBLIC_URL:default_value} からdefault_valueを抽出
                                import re
                                match = re.search(r'\$\{EDC_DATAPLANE_PUBLIC_URL:(.*?)\}', endpoint)
                                if match:
                                    endpoint = match.group(1)
                                    st.info(f"🔧 **Extracted endpoint from placeholder**: {endpoint}")
                            
                            st.success(f"✅ **EDR Endpoint**: {endpoint}")
                            st.info(f"🔑 **Authorization Token**: {auth_header[:20]}...")
                            break
                    else:
                        # まだEDRが発行されていない場合
                        if st.session_state.get("debug_mode"):
                            st.info(f"EDR取得試行 {attempt}/15 (HTTP {edr_response.status_code})")
                        
                except Exception as e:
                    if st.session_state.get("debug_mode"):
                        st.warning(f"EDR取得試行 {attempt}/15 で例外: {e}")
                    continue

            if not endpoint or not auth_header:
                st.error("❌ EDRを取得できませんでした（タイムアウト）。")
                return

        # ---- データフェッチ（サンプルに基づく正しい方法）----
        st.write("**📡 Fetching data from provider...**")
        st.write(f"- **Endpoint**: `{endpoint}`")
        
        try:
            with st.spinner("Fetching data..."):
                # サンプルに記載されている方法: エンドポイントにAuthorizationヘッダーでアクセス
                data_response = requests.get(
                    endpoint,
                    headers={"Authorization": auth_header},
                    timeout=15
                )

            st.write(f"**Response Status**: {data_response.status_code}")

            if data_response.status_code == 200:
                st.success("🎉 **Data transfer completed successfully!**")

                # JSON とテキストの両対応
                try:
                    json_data = data_response.json()
                    st.subheader("📊 Transferred Data (JSON)")
                    st.json(json_data)
                except Exception:
                    st.subheader("📄 Transferred Data (Text)")
                    st.text_area("Data Content:", data_response.text, height=200)

                st.success("✅ **End-to-End EDC Data Transfer Flow Completed!**")
                st.info("🔄 **Flow Summary**: Asset → Policy → Contract Offer → Catalog → Negotiation → Agreement → Transfer → Data Access")

            elif data_response.status_code == 401:
                st.error("🔐 Authorization failed - Token may have expired.")
                st.info("💡 新しい契約を交渉してトークンを更新してください。")
            elif data_response.status_code == 404:
                st.error("🔍 Data not found - Asset may not exist.")
            else:
                st.error(f"❌ Failed to fetch data: HTTP {data_response.status_code}")
                st.text(f"Response: {data_response.text}")

        except Exception as e:
            st.error(f"❌ Error fetching data: {e}")


def main():
    """Main application"""
    init_page()
    
    # Service status indicators
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            edc_response = requests.get(f"{EDC_MANAGEMENT}/management/v3/assets", timeout=5)
            if edc_response.status_code in [200, 405]:  # 405は正常（GETメソッドが許可されていない）
                st.success("🟢 **EDC Connector:** Online")
            else:
                st.error("🔴 **EDC Connector:** Offline")
        except:
            st.error("🔴 **EDC Connector:** Offline")
    
    with col2:
        try:
            data_response = requests.get("http://data-api:8000/health", timeout=5)
            if data_response.status_code == 200:
                try:
                    response_data = data_response.json()
                    if isinstance(response_data, dict) and response_data.get("status") == "healthy":
                        st.success("🟢 **Data API:** Online")
                    else:
                        st.success("🟢 **Data API:** Online")
                except:
                    # JSONパースエラーの場合でも200ステータスなら成功とする
                    st.success("🟢 **Data API:** Online")
            else:
                st.error("🔴 **Data API:** Offline")
        except:
            st.error("🔴 **Data API:** Offline")
    
    st.markdown("---")
    
    # Role selection dropdown
    st.markdown("### 🎯 Select Your Role")
    role = st.selectbox(
        "Choose the EDC role you want to operate as:",
        ("🏭 Data Provider", "🛒 Data Consumer"),
        index=0
    )
    
    st.markdown("---")
    
    # Display operations based on selected role
    if role == "🏭 Data Provider":
        st.markdown("## 🏭 Data Provider Operations")
        st.markdown("*Create and manage your data assets, policies, and contract offers*")
        st.markdown("")
        
        create_asset()
        st.markdown("---")
        
        create_policy()
        st.markdown("---")
        
        create_contract_offer()
    
    elif role == "🛒 Data Consumer":
        st.markdown("## 🛒 Data Consumer Operations")
        st.markdown("*Discover and consume data from providers*")
        st.markdown("")
        
        fetch_catalog()
        st.markdown("---")
        
        negotiate_contract()
        st.markdown("---")
        
        data_transfer()

if __name__ == "__main__":
    main()